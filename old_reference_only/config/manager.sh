#!/bin/bash
##############################################################################
#                      NMap Scan Automation Script (Manager)                 #
##############################################################################
# This script will check the db file to see if a scan is to run against the  #
# network.  If there is a scan to run, then it will generate the command     #
# that needs to be run and output it to a script.  Once the scripted command #
# is created, it will then send the data to the appropriate sensor and start #
# to run the scan.  The script that was generated will report the data back  #
# to the management console.                                                 #
##############################################################################
# Build: 003                                                                 #
# Author: Steven McGrath                                                     #
# Date of Build: 12/18/07                                                    #
##############################################################################

## Set the Globals

# This is the timezone that the scans are written in
timezone=utc

# This is the location of the configuration files.
configDir=/opt/nmap/config

# This is where the output will go.
dataDir=/opt/nmap/data

# Location for the Files on the sensor
tempDataLoc=/opt/nmap/sensor

# XML Output?
xml=Yes

# Grepable Output?
grepable=Yes

# Copy the data to an offsite location?
offSite=Yes

# FTP Informtation for offsite.
ftpUser=nmap
ftpPassword=4f2380c26638
ftpLocation=10.208.87.124


# Is the sensor remote to the system?
# Please note that "Yes" will activate ssh, so you need to make sure that you
# have a trusted keypair or RSA keys with NO PASSWORD set in order for this to work.
sensorRemote=Yes

# Set any nmap flags you want to run here.  Please note this is mostly used for tuning,
# adding thins like OS detection or version detection really slows things down!
nmapOptions_Base="--min_hostgroup 64 --initial_rtt_timeout 150 --max_rtt_timeout 200 --max_retries 1"

###### DO NOT MODIFY BELOW HERE #######

# Set the date variable so that we can use it statically.
dateOfScan=$(date +%m%d%y-%H%M%S)
scanDate=$(date +%H%Mutc)

## Now we need to figure out what scanners exist.
scanners=$(cat $configDir/scanlist.db | grep "scanner:")
numOfScanners=$(echo $scanners | wc -w)

## Also, whats considered bad to scan.
doNotScan=$(echo $(cat $configDir/dontscan.list) | awk '{gsub(/ /,",");print}')
if [ "$doNotScan" != "" ];then
    doNotScan="--exclude $doNotScan"
fi

## Lets start the scanning loop!
for ((i=1;i<=$numOfScanners;i+=1));do

    # Reset the nmapOptions Variable
    nmapOptions=$nmapOptions_Base
    
    # Lets determine the scanner and the network it scans.
    scanner=$(echo $scanners | cut -d " " -f $i | cut -d ":" -f 3)
    network=$(echo $scanners | cut -d " " -f $i | cut -d ":" -f 2)

    # XML Output
    if [ $xml == "Yes" ];then
        nmapOptions="$nmapOptions -oX $tempDataLoc/nmap-$dateOfScan-$network.xml"
    fi

    # Grepable Output
    if [ $grepable == "Yes" ];then
        nmapOptions="$nmapOptions -oG $tempDataLoc/nmap-$dateOfScan-$network.grep"
    fi
    
    # Now we need to figure out what to scan.
    scanList=$(cat $configDir/scanlist.db\
                | grep "$network:"\
                | grep -i "$scanDate:"\
                | cut -d ":" -f 3)
    
    # Lets build the NMap scan command
    scanCommand="nmap $nmapOptions $doNotScan $scanList"
    
    # Run NMap and then copy the data back to the manager
    if [ "$scanList" != "" ];then
        if [ $sensorRemote == "Yes" ];then
        
            # Debug Option, uncomment to figure out whats going on.
            echo -e "Scanning $network Network using sensor $scanner\n\t$scanCommand"
        
            ssh root@$scanner "$scanCommand" > /dev/null
            scp root@$scanner:$tempDataLoc/nmap-$dateOfScan-$network.* 
$tempDataLoc
        else
            $scanCommand > /dev/null
        fi

	mv $tempDataLoc/*.grep $dataDir/grep
	mv $tempDataLoc/*.xml $dataDir/xml

	if [ $offSite == Yes ];then
	    cp $dataDir/xml/nmap-$dateOfScan-$network.xml $tempDataLoc/nmap-$dateOfScan-$network.xml
	    touch $tempDataLoc/nmap-$dateOfScan-$network.xml_done
        nohup lftp ftp://$ftpUser:$ftpPassword@$ftpLocation/ -e "put $tempDataLoc/nmap-$dateOfScan-$network.xml;put $tempDataLoc/nmap-$dateOfScan-$network.xml_done;quit" &
        rm -f $tempDataLoc/nmap-$dateOfScan-$network.xml*
	fi
    fi
        
done
