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
use MailScanner::Config;

my ( $conn, $bconn, $sth, $bsth, $server );
my ($hostname)  = hostname;
my $server_port = 11553;
my $timeout     = 3600;

my ( $db_user, $db_pass, $baruwa_dsn );
my ($sqlite_db) = "/var/spool/MailScanner/incoming/baruwa2.db";

#DBI->trace(2,'/tmp/dbitrace.log');
sub insert_record {
    my ($message) = @_;
    $sth->execute(
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
}

sub create_backup_tables {
    eval {
        $bconn->do("PRAGMA default_synchronous = OFF");
        $bconn->do(
            "CREATE TABLE IF NOT EXISTS tm (
                timestamp TEXT NOT NULL,
                id TEXT NOT NULL,
                size INT NOT NULL,
                from_address TEXT NOT NULL,
                from_domain TEXT NOT NULL,
                to_address TEXT NOT NULL,
                to_domain TEXT NOT NULL,
                subject TEXT NOT NULL,
                clientip TEXT NOT NULL,
                spam INT NOT NULL,
                highspam INT NOT NULL,
                saspam INT NOT NULL,
                rblspam INT NOT NULL,
                whitelisted INT NOT NULL,
                blacklisted INT NOT NULL,
                sascore REAL NOT NULL,
                spamreport TEXT NOT NULL,
                virusinfected TEXT NOT NULL,
                nameinfected INT NOT NULL,
                otherinfected INT NOT NULL,
                hostname TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                headers TEXT NOT NULL, 
                actions TEXT NOT NULL,
                isquarantined INT NOT NULL,
                scaned INT NOT NULL
            )"
        );
        $bconn->do("CREATE UNIQUE INDEX id_uniq ON tm(id)");
    };
}

sub connect2db {
    $db_user = MailScanner::Config::Value('dbusername') if (!defined($db_user));
    $db_pass = MailScanner::Config::Value('dbpassword') if (!defined($db_pass));
    $baruwa_dsn = MailScanner::Config::Value('dbdsn') if (!defined($baruwa_dsn));
    eval {
        local $SIG{ALRM} = sub { die "TIMEOUT\n" };
        eval {
            alarm(5);
            $conn = DBI->connect_cached(
                $baruwa_dsn,
                $db_user, $db_pass,
                {
                    PrintError           => 0,
                    AutoCommit           => 1,
                    private_foo_cachekey => 'baruwa',
                    RaiseError           => 1
                }
            ) unless $conn and $conn->ping;
            $conn->do("SET NAMES 'utf8'");
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
            alarm(0);
        };
        alarm(0);
        die $@ if $@;
    };
    if ($@) {
        MailScanner::Log::WarnLog("Baruwa: DB init Failed: $@");
    }
}

sub log2backup {
    my ($message) = @_;

    eval {
        $bsth->execute(
            $$message{id},            $$message{actions},
            $$message{clientip},      $$message{date},
            $$message{from_address},  $$message{from_domain},
            $$message{headers},       $$message{hostname},
            $$message{highspam},      $$message{rblspam},
            $$message{saspam},        $$message{spam},
            $$message{nameinfected},  $$message{otherinfected},
            $$message{isquarantined}, $$message{sascore},
            $$message{scaned},      $$message{size},
            $$message{blacklisted},   $$message{spamreport},
            $$message{whitelisted},   $$message{subject},
            $$message{time},          $$message{timestamp},
            $$message{to_address},    $$message{to_domain},
            $$message{virusinfected}
        );
        MailScanner::Log::InfoLog("Baruwa: $$message{id}: Logged using backup DB");
    };
    if ($@) {
        MailScanner::Log::InfoLog("Baruwa: $$message{id}: backup logging failed");
    }
}


sub InitBaruwaSQL {
    my $pid = fork();
    if ($pid) {
        waitpid $pid, 0;
    }
    else {
        POSIX::setsid();
        MailScanner::Log::InfoLog("Baruwa: Starting SQL logger");
        # Close all I/O filehandles to completely detach from terminal
        open STDIN,  "</dev/null";
        open STDOUT, ">/dev/null";
        open STDERR, ">/dev/null";

        if ( !fork() ) {
            $SIG{HUP} = $SIG{INT} = $SIG{PIPE} = $SIG{TERM} = $SIG{ALRM} =
              \&ExitBaruwaSQL;
            #alarm $timeout;
            $0 = "Baruwa SQL";
            InitSQLConnections();
            BaruwaListener();
        }
        exit;
    }
}

sub ExitBaruwaSQL {
    MailScanner::Log::InfoLog("Baruwa: SQL shutting down");
    close($server);
    $conn->disconnect if $conn;
    #$bconn->disconnect if $bconn;
    exit;
}

sub RecoverFromSql {
    my $st;
    eval {
        $st = $bconn->prepare("SELECT * FROM tm");
        $st->execute();
    };
    if ($@) {
        MailScanner::Log::InfoLog("Baruwa: Backup DB recovery Failure");
        return;
    }

    my @ids;
    while ( my $message = $st->fetchrow_hashref ) {
        eval {
            insert_record($message);
            MailScanner::Log::InfoLog("Baruwa: $$message{id}: Logged to SQL from backup");
            push @ids, $$message{id};
        };
        if ($@) {
            MailScanner::Log::InfoLog("Baruwa: Backup DB insert Fail");
        }

    }

    # delete messages that have been logged
    while (@ids) {
        my @tmp_ids = splice( @ids, 0, 50 );
        my $del_ids = join q{,}, map { '?' } @tmp_ids;
        eval {
            $bconn->do( "DELETE FROM tm WHERE id IN ($del_ids)",
                undef, @tmp_ids );
        };
        if ($@) {
            MailScanner::Log::WarnLog("Baruwa: Backup DB clean temp Fail");
        }
    }
    undef @ids;
}

sub initbackup {
    eval {
        $bconn = DBI->connect_cached(
            "dbi:SQLite:$sqlite_db",
            "", "",
            {
                PrintError           => 0,
                AutoCommit           => 1,
                private_foo_cachekey => 'baruwa_backup',
                RaiseError           => 1
            }
        ) unless ($bconn);
    };
    if ($@) {
        MailScanner::Log::WarnLog("Baruwa: Backup DB init Fail");
    }

    create_backup_tables();

    eval {
        $bsth = $bconn->prepare(
            "INSERT INTO tm (
            id,actions,clientip,date,from_address,from_domain,headers,
            hostname,highspam,rblspam,saspam,spam,nameinfected,otherinfected,
            isquarantined,sascore,scaned,size,blacklisted,spamreport,
            whitelisted,subject,time,timestamp,to_address,to_domain,
            virusinfected
        )  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        ) unless $bsth;
    };
    if ($@) {
        MailScanner::Log::WarnLog("Baruwa: Backup DB prep Fail");
    }else{
        if ($conn && $conn->ping) {
            MailScanner::Log::InfoLog("Baruwa: DB conn alive, starting recovery");
            RecoverFromSql();
        }
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
    connect2db();
    initbackup();
}

sub BaruwaListener {
    my ( $message, $client, $client_address );
    while ( ( $client, $client_address ) = $server->accept() ) {
        my ( $port, $packed_ip ) = sockaddr_in($client_address);
        my $client_ip = inet_ntoa($packed_ip);
        #alarm $timeout;
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
        close $client;
        my $data = join "", @in;
        my $tmp = unpack( "u", $data );
        $message = thaw $tmp;

        next unless defined $$message{id};

        connect2db unless $conn && $conn->ping;
        eval {
            insert_record($message);
            MailScanner::Log::InfoLog("Baruwa: $$message{id}: Logged to SQL");
        };
        if ($@) {
            log2backup($message);
        }else{
            RecoverFromSql();
        }
        $message = undef;
    }
}

sub EndBaruwaSQL {
    MailScanner::Log::InfoLog("Baruwa: Shutting down SQL logger");
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

    unless ( defined( $$message{utf8subject} ) and $$message{utf8subject} ) {
        $$message{utf8subject} = '';
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
    $msg{subject}       = $message->{utf8subject};
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
    $msg{scaned}      = $message->{scanmail};

    my $f = freeze \%msg;
    my $p = pack( "u", $f );

    my $client = IO::Socket::INET->new(
        PeerAddr => '127.0.0.1',
        PeerPort => $server_port,
        Proto    => 'tcp',
        Type     => SOCK_STREAM
    );
    if ($client) {
        MailScanner::Log::InfoLog("Baruwa: Logging message $msg{id} to SQL");
        print $client $p;
        print $client "END\n";
        close $client;
    }else{
        MailScanner::Log::InfoLog("Baruwa: Sending message $msg{id} to server failed, using backup");
        initbackup() unless $bconn;
        log2backup(\%msg);
    }
}

1;
