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
use Net::CIDR;

my ( %Whitelist, %Blacklist );
my @WhiteIPs = ();
my @BlackIPs = ();
my ( $wtime, $btime );
my ($refresh_time) = 10;

sub PopulateList {
    my ( $type, $list, $ips ) = @_;
    @$ips = ();

    my ($db_name) = 'baruwa';
    my ($db_host) = 'localhost';
    my ($db_user) = 'baruwa';
    my ($db_pass) = '';

    my ( $conn, $sth, $to_address, $from_address, $count );

    $conn = DBI->connect( "DBI:mysql:database=$db_name;host=$db_host",
        $db_user, $db_pass, { PrintError => 0, AutoCommit => 1 } );
    if ( !$conn ) {
        MailScanner::Log::WarnLog( "Baruwa Lists db conn init failue: %s",
            $DBI::errstr );
    }
    $sth = $conn->prepare(
        "SELECT to_address, from_address FROM lists where list_type = ?");
    $sth->execute($type);
    $sth->bind_columns( undef, \$to_address, \$from_address );
    $count = 0;
    while ( $sth->fetch() ) {
        if ( $from_address =~ /^([.:\da-f]+)\s*\/\s*([.:\da-f]+)$/ ) {
            my ( $network, $bits, $count, $mcount );
            ( $network, $bits ) = ( $1, $2 );
            my @count = split( /\./, $network );
            $count = @count;
            $network .= '.0' x ( 4 - $count );
            my @mcount = split( /\./, $bits );
            $mcount = @mcount;
            if ( $mcount == 4 ) {
                my $range = Net::CIDR::addrandmask2cidr( $network, $bits );
                push( @$ips, $range );
            }
            else {
                push( @$ips, "$network/$bits" );
            }
        }
        elsif ( $from_address =~ /^[.:\da-f]+\s*-\s*[.:\da-f]+$/ ) {
            $from_address =~ s/\s*//g;
            my @cidr = Net::CIDR::range2cidr($from_address);
            foreach my $cidr (@cidr) {
                push( @$ips, $cidr );
            }
        }
        else {
            $list->{ lc($to_address) }{ lc($from_address) } = 1;
        }
        $count++;
    }
    $sth->finish();
    $conn->disconnect();
    return $count;
}

sub LookupAddress {
    my ( $message, $list, $ips ) = @_;

    return 0 unless $message;

    my ( $from, $fromdomain, @todomain, $todomain, @to, $to, $ip );
    $from       = $message->{from};
    $fromdomain = $message->{fromdomain};
    @todomain   = @{ $message->{todomain} };
    $todomain   = $todomain[0];
    @to         = @{ $message->{to} };
    $to         = $to[0];
    $ip         = $message->{clientip};

    return 1 if Net::CIDR::cidrlookup( $ip, @$ips );
    return 1 if $list->{$to}{$from};
    return 1 if $list->{$to}{$fromdomain};
    return 1 if $list->{$to}{$ip};
    return 1 if $list->{$to}{'any'};
    return 1 if $list->{$todomain}{$from};
    return 1 if $list->{$todomain}{$fromdomain};
    return 1 if $list->{$todomain}{$ip};
    return 1 if $list->{$todomain}{'any'};
    return 1 if $list->{'any'}{$from};
    return 1 if $list->{'any'}{$fromdomain};
    return 1 if $list->{'any'}{$ip};

    return 0;
}

sub InitBaruwaWhitelist {
    MailScanner::Log::InfoLog("Starting Baruwa whitelists");
    my $total = PopulateList( 1, \%Whitelist, \@WhiteIPs );
    MailScanner::Log::InfoLog( "Read %d whitelist items", $total );
    MailScanner::Log::InfoLog( "Ip blocks whitelisted: @WhiteIPs" );
    $wtime = time();
}

sub EndBaruwaWhitelist {
    MailScanner::Log::InfoLog("Shutting down Baruwa whitelists");
}

sub BaruwaWhitelist {
    if ( ( time() - $wtime ) >= ( $refresh_time * 60 ) ) {
        MailScanner::Log::InfoLog("Baruwa whitelist refresh time reached");
        InitBaruwaWhitelist();
    }
    my ($message) = @_;
    return LookupAddress( $message, \%Whitelist, \@WhiteIPs );
}

sub InitBaruwaBlacklist {
    MailScanner::Log::InfoLog("Starting Baruwa blacklists");
    my $total = PopulateList( 2, \%Blacklist, \@BlackIPs );
    MailScanner::Log::InfoLog( "Read %d blacklist items", $total );
    MailScanner::Log::InfoLog( "Ip blocks blacklisted: @BlackIPs" );
    $btime = time();
}

sub EndBaruwaBlacklist {
    MailScanner::Log::InfoLog("Shutting down Baruwa blacklists");
}

sub BaruwaBlacklist {
    if ( ( time() - $btime ) >= ( $refresh_time * 60 ) ) {
        MailScanner::Log::InfoLog("Baruwa blacklist refresh time reached");
        InitBaruwaBlacklist();
    }
    my ($message) = @_;
    return LookupAddress( $message, \%Blacklist, \@BlackIPs );
}

1;
