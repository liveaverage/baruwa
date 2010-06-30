package MailScanner::CustomConfig;

use strict;
use Sys::Hostname;
use Storable(qw[freeze thaw]);
use POSIX;
use Socket;
use DBI;
use CouchDB::Client;

my ($db);
my ($bdb);
my ($sth);
my ($couchhost) = "127.0.0.1";
my ($couchport) = "5984";
my ($sqlite_db) = "/var/spool/MailScanner/incoming/baruwa.db";
my ($hostname)  = hostname;
my $loop        = inet_aton("127.0.0.1");
my $server_port = 11554;
my $timeout     = 3600;

sub InitBaruwaLogging {
    my $pid = fork();
    if ($pid) {
        waitpid $pid, 0;
        MailScanner::Log::InfoLog("Starting Baruwa CouchDB logger");
    }
    else {
        POSIX::setsid();
        if ( !fork() ) {
            $SIG{HUP} = $SIG{INT} = $SIG{PIPE} = $SIG{TERM} = $SIG{ALRM} =
              \&ExitBaruwaLogging;
            alarm $timeout;
            $0 = "Baruwa CouchDB";
            InitCouchConnection();
            ListenForMessages();
        }
        exit;
    }
}

sub RecoverFromSql {
    if ($db) {
        my $st = $bdb->prepare("SELECT * FROM temp_couch")
          or MailScanner::Log::WarnLog( "Unable to prepare query: %s",
            $DBI::errstr );
        $st->execute();
        my @ids;
        while ( my $msg = $st->fetchrow_hashref ) {
            my $msgid = $$msg{id};
            delete $$msg{id};
            eval { my $doc = $db->newDoc( $msgid, undef, $msg )->create };
            if ( !$@ ) {
                MailScanner::Log::InfoLog(
                    "$msgid: Logged to Baruwa CouchDB from SQL Fallback");
                push @ids, $msgid;
            }
        }
        while (@ids) {
            my @tmp_ids = splice( @ids, 0, 50 );
            my $del_ids = join q{,}, map { '?' } @tmp_ids;
            $bdb->do( "DELETE FROM temp_couch WHERE id IN ($del_ids)",
                undef, @tmp_ids )
              or
              MailScanner::Log::WarnLog( "Unable to delete: %s", $DBI::errstr );
        }
    }
}

sub PrepSqlite {
    $bdb = DBI->connect( "dbi:SQLite:$sqlite_db", "", "", { PrintError => 0 } );
    if ( !$bdb ) {
        MailScanner::Log::WarnLog(
            "Unable to initialise database connection: %s", $DBI::errstr );
    }
    else {
        $bdb->do("PRAGMA default_synchronous = OFF");
        $bdb->do(
            "CREATE TABLE temp_couch (timestamp TEXT, id TEXT, 
			size INT, from_address TEXT, from_domain TEXT, to_address TEXT, 
			to_domain TEXT, subject TEXT, clientip TEXT, 
			archiveplaces TEXT, isspam INT, ishigh INT, 
			issaspam INT, isrblspam INT, spamwhitelisted INT, 
			spamblacklisted INT, sascore REAL, spamreport TEXT, 
			virusinfected TEXT, nameinfected INT, otherinfected INT, 
			hostname TEXT, date TEXT, time TEXT, headers TEXT, 
			actions TEXT, quarantined INT, scanmail INT)"
        );
        $bdb->do("CREATE UNIQUE INDEX id_uniq ON temp_couch(id)");
        RecoverFromSql();
        $sth = $bdb->prepare( "
			INSERT INTO temp_couch (
			timestamp,id,size,from_address,from_domain,to_address,to_domain,subject,
			clientip,archiveplaces,isspam,ishigh,issaspam,isrblspam,spamwhitelisted,
			spamblacklisted,sascore,spamreport,virusinfected,nameinfected,otherinfected,
			hostname,date,time,headers,actions,quarantined,scanmail)  
			VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" )
          or MailScanner::Log::WarnLog( "Unable to prepare insert query: %s",
            $DBI::errstr );
    }
}

sub InitCouchConnection() {
    socket( SERVER, PF_INET, SOCK_STREAM, getprotobyname("tcp") );
    setsockopt( SERVER, SOL_SOCKET, SO_REUSEADDR, 1 );
    my $addr = sockaddr_in( $server_port, $loop );
    bind( SERVER, $addr ) or exit;
    listen( SERVER, SOMAXCONN ) or exit;

    my $couch = CouchDB::Client->new( uri => "http://$couchhost:$couchport" );
    if ( !$couch->testConnection ) {
        MailScanner::Log::InfoLog("CouchDB server could not be reached");
    }
    else {
        $db = $couch->newDB('baruwa');
    }
    PrepSqlite();
}

sub ExitBaruwaLogging {
    close(SERVER);
    eval { $bdb->disconnect; };
    exit;
}

sub ListenForMessages {
    my $message;
    while ( my $cli = accept( CLIENT, SERVER ) ) {
        my ( $port, $packed_ip ) = sockaddr_in($cli);
        my $dotted_quad = inet_ntoa($packed_ip);
        alarm $timeout;
        if ( $dotted_quad ne "127.0.0.1" ) {
            close CLIENT;
            next;
        }
        my @in;
        while (<CLIENT>) {
            last if /^END$/;
            ExitBaruwaLogging if /^EXIT$/;
            chop;
            push @in, $_;
        }
        my $data = join "", @in;
        my $tmp = unpack( "u", $data );
        $message = thaw $tmp;

        next unless defined $$message{id};

        my $msgid = $$message{id};
        delete $$message{id};
        InitCouchConnection unless $db;
        eval { my $doc = $db->newDoc( $msgid, undef, $message )->create; };
        if ($@) {
            MailScanner::Log::InfoLog(
"$msgid: Baruwa CouchDB Cannot create record - falling back on sql"
            );
            $sth->execute(
                $$message{timestamp},       $msgid,
                $$message{size},            $$message{from_address},
                $$message{from_domain},     $$message{to_address},
                $$message{to_domain},       $$message{subject},
                $$message{clientip},        $$message{archiveplaces},
                $$message{isspam},          $$message{ishigh},
                $$message{issaspam},        $$message{isrblspam},
                $$message{spamwhitelisted}, $$message{spamblacklisted},
                $$message{sascore},         $$message{spamreport},
                $$message{virusinfected},   $$message{nameinfected},
                $$message{otherinfected},   $$message{hostname},
                $$message{date},            $$message{time},
                $$message{headers},         $$message{actions},
                $$message{quarantined},     $$message{scanmail}
            ) or MailScanner::Log::WarnLog( "lalalala: %s", $DBI::errstr );
        }
        else {
            MailScanner::Log::InfoLog("$msgid: Logged to Baruwa CouchDB");
            RecoverFromSql();
        }
        $message = undef;
    }
}

sub EndBaruwaLogging {
    MailScanner::Log::InfoLog("Shutting down Baruwa CouchDB logger");
    socket( TO_SERVER, PF_INET, SOCK_STREAM, getprotobyname("tcp") );
    my $addr = sockaddr_in( $server_port, $loop );
    connect( TO_SERVER, $addr ) or return;
    print TO_SERVER "EXIT\n";
    close TO_SERVER;
}

sub BaruwaLogging {
    my ($message) = @_;

    return unless $message;

    my (%rcpts);
    map { $rcpts{$_} = 1; } @{ $message->{to} };
    @{ $message->{to} } = keys %rcpts;

    my $spamreport = $message->{spamreport};
    $spamreport =~ s/\n/ /g;
    $spamreport =~ s/\t//g;

    my ($quarantined);
    $quarantined = 0;
    if ( ( scalar( @{ $message->{quarantineplaces} } ) ) +
        ( scalar( @{ $message->{spamarchive} } ) ) > 0 )
    {
        $quarantined = 1;
    }

    my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) =
      localtime();
    my ($timestamp) = sprintf(
        "%d-%02d-%02d %02d:%02d:%02d",
        $year + 1900,
        $mon + 1, $mday, $hour, $min, $sec
    );

    my ($date) = sprintf( "%d-%02d-%02d",   $year + 1900, $mon + 1, $mday );
    my ($time) = sprintf( "%02d:%02d:%02d", $hour,        $min,     $sec );

    my $clientip = $message->{clientip};
    $clientip =~ s/^(\d+\.\d+\.\d+\.\d+)(\.\d+)$/$1/;

    if ( $spamreport =~ /USER_IN_WHITELIST/ ) {
        $message->{spamwhitelisted} = 1;
    }
    if ( $spamreport =~ /USER_IN_BLACKLIST/ ) {
        $message->{spamblacklisted} = 1;
    }

    my ( $todomain, @todomain );
    @todomain = @{ $message->{todomain} };
    $todomain = $todomain[0];

    # Place all data into %msg
    my %msg;
    $msg{timestamp}       = $timestamp;
    $msg{id}              = $message->{id};
    $msg{size}            = $message->{size};
    $msg{from_address}    = $message->{from};
    $msg{from_domain}     = $message->{fromdomain};
    $msg{to_address}      = join( ",", @{ $message->{to} } );
    $msg{to_domain}       = $todomain;
    $msg{subject}         = $message->{subject};
    $msg{clientip}        = $clientip;
    $msg{archiveplaces}   = join( ",", @{ $message->{archiveplaces} } );
    $msg{isspam}          = $message->{isspam};
    $msg{ishigh}          = $message->{ishigh};
    $msg{issaspam}        = $message->{issaspam};
    $msg{isrblspam}       = $message->{isrblspam};
    $msg{spamwhitelisted} = $message->{spamwhitelisted};
    $msg{spamblacklisted} = $message->{spamblacklisted};
    $msg{sascore}         = $message->{sascore};
    $msg{spamreport}      = $spamreport;
    $msg{virusinfected}   = $message->{virusinfected};
    $msg{nameinfected}    = $message->{nameinfected};
    $msg{otherinfected}   = $message->{otherinfected};
    $msg{hostname}        = $hostname;
    $msg{date}            = $date;
    $msg{time}            = $time;
    $msg{headers}         = join( "\n", @{ $message->{headers} } );
    $msg{actions}         = $message->{actions};
    $msg{quarantined}     = $quarantined;
    $msg{scanmail}        = $message->{scanmail};

    my $f = freeze \%msg;
    my $p = pack( "u", $f );

    while (1) {
        socket( TO_SERVER, PF_INET, SOCK_STREAM, getprotobyname("tcp") );
        my $addr = sockaddr_in( $server_port, $loop );
        connect( TO_SERVER, $addr ) and last;
        InitBaruwaLogging();
        sleep 5;
    }

    MailScanner::Log::InfoLog("Logging message $msg{id} to CouchDB");
    print TO_SERVER $p;
    print TO_SERVER "END\n";
    close TO_SERVER;
}

1;
