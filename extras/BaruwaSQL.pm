# 
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
package MailScanner::CustomConfig;

use strict;
use Sys::Hostname;
use Storable(qw[freeze thaw]);
use POSIX;
use IO::Socket;
use DBI;

my ( $conn, $bconn, $sth, $bsth, $server );
my ($hostname)  = hostname;
my $server_port = 11553;
my $timeout     = 3600;

my ($db_name) = 'baruwa';
my ($db_host) = 'localhost';
my ($db_user) = 'baruwa';
my ($db_pass) = '';
my ($sqlite_db) = "/var/spool/MailScanner/incoming/baruwa2.db";

#DBI->trace(2,'/tmp/dbitrace.log');

sub InitBaruwaSQL {
    my $pid = fork();
    if ($pid) {
        waitpid $pid, 0;
        MailScanner::Log::InfoLog("Starting Baruwa SQL logger");
    }
    else {
        POSIX::setsid();

        # Close all I/O filehandles to completely detach from terminal
        open STDIN,  "</dev/null";
        open STDOUT, ">/dev/null";
        open STDERR, ">/dev/null";

        if ( !fork() ) {
            $SIG{HUP} = $SIG{INT} = $SIG{PIPE} = $SIG{TERM} = $SIG{ALRM} =
              \&ExitBaruwaSQL;
            alarm $timeout;
            $0 = "Baruwa SQL";
            InitSQLConnections();
            BaruwaListener();
        }
        exit;
    }
}

sub ExitBaruwaSQL {
    close($server);
    $conn->disconnect;
    $bconn->disconnect;
    exit;
}

sub RecoverFromSql {
    my $st = $bconn->prepare("SELECT * FROM temp_messages")
      or MailScanner::Log::WarnLog( "Baruwa SQL backup select failure: %s",
        $DBI::errstr );
    $st->execute();
    my @ids;
    while ( my $message = $st->fetchrow_hashref ) {
        my $rv = $sth->execute(
            $$message{id},            $$message{actions},
            $$message{clientip},      $$message{date},
            $$message{from_address},  $$message{from_domain},
            $$message{headers},       $$message{hostname},
            $$message{highspam},      $$message{rblspam},
            $$message{saspam},        $$message{spam},
            $$message{nameinfected},  $$message{otherinfected},
            $$message{isquarantined}, $$message{sascore},
            $$message{scaned},        $$message{size},
            $$message{blacklisted},   $$message{spamreport},
            $$message{whitelisted},   $$message{subject},
            $$message{time},          $$message{timestamp},
            $$message{to_address},    $$message{to_domain},
            $$message{virusinfected}
        );
        if ($rv) {
            MailScanner::Log::InfoLog(
                "$$message{id}: Logged to Baruwa SQL from backup");
            push @ids, $$message{id};
        }
    }
    while (@ids) {
        my @tmp_ids = splice( @ids, 0, 50 );
        my $del_ids = join q{,}, map { '?' } @tmp_ids;
        $bconn->do( "DELETE FROM temp_messages WHERE id IN ($del_ids)",
            undef, @tmp_ids )
          or
          MailScanner::Log::WarnLog( "Baruwa SQL backup clean temp failure: %s",
            $DBI::errstr );
    }
    undef @ids;
}

sub PrepSqlite {
    $bconn =
      DBI->connect( "dbi:SQLite:$sqlite_db", "", "",
        { PrintError => 0, AutoCommit => 1 } );
    if ( !$bconn ) {
        MailScanner::Log::WarnLog( "Baruwa SQL Backup conn init failure: %s",
            $DBI::errstr );
    }
    else {
        $bconn->do("PRAGMA default_synchronous = OFF");
        $bconn->do(
            "CREATE TABLE temp_messages (timestamp TEXT, id TEXT, 
            size INT, from_address TEXT, from_domain TEXT, to_address TEXT, 
            to_domain TEXT, subject TEXT, clientip TEXT, spam INT, highspam INT,
            saspam INT, rblspam INT, whitelisted INT, blacklisted INT, 
            sascore REAL, spamreport TEXT, virusinfected TEXT, nameinfected INT,
            otherinfected INT, hostname TEXT, date TEXT, time TEXT, headers TEXT, 
            actions TEXT, isquarantined INT, scaned INT)"
        );
        $bconn->do("CREATE UNIQUE INDEX id_uniq ON temp_messages(id)");
        RecoverFromSql();
        $bsth = $bconn->prepare( "
            INSERT INTO temp_messages (
            id,actions,clientip,date,from_address,from_domain,headers,
            hostname,highspam,rblspam,saspam,spam,nameinfected,otherinfected,
            isquarantined,sascore,scaned,size,blacklisted,spamreport,
            whitelisted,subject,time,timestamp,to_address,to_domain,
            virusinfected
        )  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" )
          or MailScanner::Log::WarnLog( "Baruwa SQL Backup Q Prep failure: %s",
            $DBI::errstr );
    }
}

sub InitSQLConnections {
    $server = IO::Socket::INET->new(
        LocalAddr => '127.0.0.1',
        LocalPort => $server_port,
        Proto     => 'tcp',
        Listen    => SOMAXCONN,
        Reuse     => 1
    ) or exit;
    eval {
        $conn = DBI->connect( "DBI:mysql:database=$db_name;host=$db_host",
            $db_user, $db_pass, { PrintError => 0, AutoCommit => 1 } );
        $sth = $conn->prepare(
            "INSERT INTO messages (
            id,actions,clientip,date,from_address,from_domain,
            headers,hostname,highspam,rblspam,saspam,spam,
            nameinfected,otherinfected,isquarantined,sascore,
            scaned,size,blacklisted,spamreport,whitelisted,
            subject,time,timestamp,to_address,to_domain,
            virusinfected
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        );
    };
    if ($@) {
        MailScanner::Log::WarnLog( "Baruwa SQL conn init failure: %s",
            $DBI::errstr );

    }
    PrepSqlite();
}

sub BaruwaListener {
    my ($message, $client, $client_address);
    while ( ( $client, $client_address ) = $server->accept() ) {
        my ( $port, $packed_ip ) = sockaddr_in($client_address);
        my $client_ip = inet_ntoa($packed_ip);
        alarm $timeout;
        if ( $client_ip ne '127.0.0.1' ) {
            close($client);
            next;
        }

        my @in;
        while (<$client>) {
            last if /^END$/;
            ExitBaruwaSQL if /^EXIT$/;
            chop;
            push @in, $_;
        }

        my $data = join "", @in;
        my $tmp = unpack( "u", $data );
        $message = thaw $tmp;

        next unless defined $$message{id};

        InitSQLConnections unless $conn->ping;
        my $rv = $sth->execute(
            $$message{id},            $$message{actions},
            $$message{clientip},      $$message{date},
            $$message{from_address},  $$message{from_domain},
            $$message{headers},       $$message{hostname},
            $$message{highspam},      $$message{rblspam},
            $$message{saspam},        $$message{spam},
            $$message{nameinfected},  $$message{otherinfected},
            $$message{isquarantined}, $$message{sascore},
            $$message{scanmail},      $$message{size},
            $$message{blacklisted},   $$message{spamreport},
            $$message{whitelisted},   $$message{subject},
            $$message{time},          $$message{timestamp},
            $$message{to_address},    $$message{to_domain},
            $$message{virusinfected}
        );
        if ($rv) {
            MailScanner::Log::InfoLog("$$message{id}: Logged to Baruwa SQL");
        }
        else {
            MailScanner::Log::InfoLog(
                "$$message{id}: Baruwa SQL using backup"
            );
            $bsth->execute(
                $$message{id},            $$message{actions},
                $$message{clientip},      $$message{date},
                $$message{from_address},  $$message{from_domain},
                $$message{headers},       $$message{hostname},
                $$message{highspam},      $$message{rblspam},
                $$message{saspam},        $$message{spam},
                $$message{nameinfected},  $$message{otherinfected},
                $$message{isquarantined}, $$message{sascore},
                $$message{scanmail},      $$message{size},
                $$message{blacklisted},   $$message{spamreport},
                $$message{whitelisted},   $$message{subject},
                $$message{time},          $$message{timestamp},
                $$message{to_address},    $$message{to_domain},
                $$message{virusinfected}
              )
              or MailScanner::Log::InfoLog(
                "$$message{id}: backup logging failure: %s", $DBI::errstr );
        }
        $message = undef;
    }
}

sub EndBaruwaSQL {
    MailScanner::Log::InfoLog("Shutting down Baruwa SQL logger");
    my $client = IO::Socket::INET->new(
        PeerAddr => '127.0.0.1',
        PeerPort => $server_port,
        Proto    => 'tcp',
        Type     => SOCK_STREAM
    ) or return;
    print $client "EXIT\n";
    close($client);
}

sub BaruwaSQL {
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
        $message->{whitelisted} = 1;
    }
    if ( $spamreport =~ /USER_IN_BLACKLIST/ ) {
        $message->{blacklisted} = 1;
    }

    my ( $todomain, @todomain );
    @todomain = @{ $message->{todomain} };
    $todomain = $todomain[0];

    unless ( defined( $$message{actions} ) and $$message{actions} ) {
        $$message{actions} = 'deliver';
    }

    unless ( defined( $$message{isrblspam} ) and $$message{isrblspam} ) {
        $$message{isrblspam} = 0;
    }
    unless ( defined( $$message{isspam} ) and $$message{isspam} ) {
        $$message{isspam} = 0;
    }

    unless ( defined( $$message{issaspam} ) and $$message{issaspam} ) {
        $$message{issaspam} = 0;
    }

    unless ( defined( $$message{ishigh} ) and $$message{ishigh} ) {
        $$message{ishigh} = 0;
    }

    unless ( defined( $$message{spamblacklisted} )
        and $$message{spamblacklisted} )
    {
        $$message{spamblacklisted} = 0;
    }

    unless ( defined( $$message{spamwhitelisted} )
        and $$message{spamwhitelisted} )
    {
        $$message{spamwhitelisted} = 0;
    }

    unless ( defined( $$message{sascore} ) and $$message{sascore} ) {
        $$message{sascore} = 0;
    }

    unless ( defined( $$message{subject} ) and $$message{subject} ) {
        $$message{subject} = '';
    }

    unless ( defined($spamreport) and $spamreport ) {
        $spamreport = '';
    }

    my %msg;
    $msg{timestamp}     = $timestamp;
    $msg{id}            = $message->{id};
    $msg{size}          = $message->{size};
    $msg{from_address}  = $message->{from};
    $msg{from_domain}   = $message->{fromdomain};
    $msg{to_address}    = join( ",", @{ $message->{to} } );
    $msg{to_domain}     = $todomain;
    $msg{subject}       = $message->{subject};
    $msg{clientip}      = $clientip;
    $msg{spam}          = $message->{isspam};
    $msg{highspam}      = $message->{ishigh};
    $msg{saspam}        = $message->{issaspam};
    $msg{rblspam}       = $message->{isrblspam};
    $msg{whitelisted}   = $message->{spamwhitelisted};
    $msg{blacklisted}   = $message->{spamblacklisted};
    $msg{sascore}       = $message->{sascore};
    $msg{spamreport}    = $spamreport;
    $msg{virusinfected} = $message->{virusinfected};
    $msg{nameinfected}  = $message->{nameinfected};
    $msg{otherinfected} = $message->{otherinfected};
    $msg{hostname}      = $hostname;
    $msg{date}          = $date;
    $msg{time}          = $time;
    $msg{headers}       = join( "\n", @{ $message->{headers} } );
    $msg{actions}       = $message->{actions};
    $msg{isquarantined} = $quarantined;
    $msg{scanmail}      = $message->{scanmail};

    my $f = freeze \%msg;
    my $p = pack( "u", $f );

    my $client_socket;
    while (1) {
        $client_socket = IO::Socket::INET->new(
            PeerAddr => '127.0.0.1',
            PeerPort => $server_port,
            Proto    => 'tcp',
            Type     => SOCK_STREAM
        ) and last;
        InitBaruwaSQL();
        sleep 5;
    }

    MailScanner::Log::InfoLog("Logging message $msg{id} to Baruwa SQL");
    print $client_socket $p;
    print $client_socket "END\n";
    close $client_socket;
}

1;
