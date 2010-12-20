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
use DBI;

my ($db_name) = 'baruwa';
my ($db_host) = 'localhost';
my ($db_user) = 'baruwa';
my ($db_pass) = '';

my ($refresh_time) = 60;
my ( $ltime, $htime );
my ( %Lowscores, %Highscores, %ScanList );

my $high_query = <<END;
SELECT DISTINCT(email),sa_high_score AS score,is_superuser FROM 
auth_user, profiles WHERE auth_user.id = profiles.user_id AND 
sa_high_score > 0 UNION SELECT address AS email,sa_high_score,0 
FROM user_addresses AS a, profiles AS b WHERE enabled=1 AND 
sa_high_score > 0 AND a.user_id = b.user_id
END

my $low_query = <<END;
SELECT DISTINCT(email),sa_low_score AS score, is_superuser FROM 
auth_user, profiles WHERE auth_user.id = profiles.user_id AND 
sa_low_score > 0 UNION SELECT address AS email,sa_low_score,0 
FROM user_addresses AS a, profiles AS b WHERE enabled=1 AND 
sa_low_score > 0 AND a.user_id = b.user_id
END

my $scan_query = <<END;
SELECT DISTINCT(email),scan_mail,is_superuser FROM
auth_user, profiles WHERE auth_user.id = profiles.user_id 
UNION SELECT address AS email,scan_mail,0 FROM 
user_addresses AS a, profiles AS b WHERE enabled=1 
AND a.user_id = b.user_id
END

sub PopulateScores {
    my ( $type, $list ) = @_;
    my ( $conn, $sth, $email, $spamscore, $query, $count, $isadmin );

    $conn = DBI->connect( "DBI:mysql:database=$db_name;host=$db_host",
        $db_user, $db_pass, { PrintError => 0, AutoCommit => 1 } );
    if ( !$conn ) {
        MailScanner::Log::WarnLog( "Baruwa Settings conn init failue: %s",
            $DBI::errstr );
    }
    if ( $type == 1 ) {
        $query = $low_query;
    }
    else {
        $query = $high_query;
    }

    $sth = $conn->prepare($query);
    $sth->execute();
    $sth->bind_columns( undef, \$email, \$spamscore, \$isadmin );
    $count = 0;
    while ( $sth->fetch() ) {
        $list->{ lc($email) } = $spamscore;
        if ($isadmin) {
            $list->{'admin'} = $spamscore;
        }
        $count++;
    }
    $sth->finish();
    $conn->disconnect();
    return $count;
}

sub CheckScores {
    my ( $type, $message, $scores ) = @_;

    return 0 unless $message;

    my ( $todomain, @to, $to, @todomain );

    @to       = @{ $message->{to} };
    @todomain = @{ $message->{todomain} };
    $to       = $to[0];
    $todomain = $todomain[0];

    return $scores->{$to}       if $scores->{$to};
    return $scores->{$todomain} if $scores->{$todomain};
    return $scores->{"admin"}   if $scores->{"admin"};

    if ( $type == 1 ) {
        return 5;
    }
    else {
        return 10;
    }
}

sub InitBaruwaLowScore {
    MailScanner::Log::InfoLog("Baruwa - Populating spam score settings");
    my $total = PopulateScores( 1, \%Lowscores );
    if ($total) {
        MailScanner::Log::InfoLog( "Read %d spam score settings", $total );
    }
    else {
        MailScanner::Log::InfoLog(
            "no spam score settings found using defaults");
    }
    $ltime = time();
}

sub InitBaruwaHighScore {
    MailScanner::Log::InfoLog("Baruwa - Populating high spam score settings");
    my $total = PopulateScores( 2, \%Highscores );
    if ($total) {
        MailScanner::Log::InfoLog( "Read %d high spam score settings", $total );
    }
    else {
        MailScanner::Log::InfoLog(
            "no high spam score settings found using defaults");
    }
    $htime = time();
}

sub EndBaruwaLowScore {
    MailScanner::Log::InfoLog("Shutting down Baruwa spam score settings");
}

sub EndBaruwaHighScore {
    MailScanner::Log::InfoLog("Shutting down Baruwa high spam score settings");
}

sub BaruwaLowScore {
    if ( ( time() - $ltime ) >= ( $refresh_time * 60 ) ) {
        MailScanner::Log::InfoLog(
            "Baruwa - spam score setting refresh time reached");
        InitBaruwaLowScore();
    }
    my ($message) = @_;
    return CheckScores( 1, $message, \%Lowscores );
}

sub BaruwaHighScore {
    if ( ( time() - $htime ) >= ( $refresh_time * 60 ) ) {
        MailScanner::Log::InfoLog(
            "Baruwa - high spam score setting refresh time reached");
        InitBaruwaHighScore();
    }
    my ($message) = @_;
    return CheckScores( 2, $message, \%Highscores );
}

sub PopulateScanList {
    my ($list) = @_;

    my ( $conn, $sth, $count, $shouldscan, $isadmin, $email );

    $conn = DBI->connect( "DBI:mysql:database=$db_name;host=$db_host",
        $db_user, $db_pass, { PrintError => 0, AutoCommit => 1 } );
    if ( !$conn ) {
        MailScanner::Log::WarnLog( "Baruwa Scan Settings conn init failue: %s",
            $DBI::errstr );
    }

    $sth = $conn->prepare($scan_query);
    $sth->execute();
    $sth->bind_columns( undef, \$email, \$shouldscan, \$isadmin );
    $count = 0;
    while ( $sth->fetch() ) {
        $list->{ lc($email) } = $shouldscan;
        if ($isadmin) {
            $list->{'admin'} = $shouldscan;
        }
        $count++;
    }
    $sth->finish();
    $conn->disconnect();
    return $count;
}

sub CheckShouldScan {
    my ( $message, $list ) = @_;

    return 0 unless $message;

    my ( $todomain, @to, $to, @todomain );

    @to       = @{ $message->{to} };
    @todomain = @{ $message->{todomain} };
    $to       = $to[0];
    $todomain = $todomain[0];

    return $list->{$to}       if $list->{$to};
    return $list->{$todomain} if $list->{$todomain};
    return $list->{"admin"}   if $list->{"admin"};
    return 1;
}

sub InitBaruwaShouldScan {
    MailScanner::Log::InfoLog("Starting Baruwa scanning settings");
    my $total = PopulateScanList( \%ScanList );
    MailScanner::Log::InfoLog( "Read %d settings", $total );
}

sub EndBaruwaShouldScan {
    MailScanner::Log::InfoLog("Shutting down Baruwa scanning settings");
}

sub BaruwaShouldScan {
    my ($message) = @_;
    return CheckShouldScan( $message, \%ScanList );
}

1;
