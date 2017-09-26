##### Declare Simulator
set ns [new Simulator]

##### Setting output file
set tracefile [open Tahoe1_[lindex $argv 1].tr w]
$ns trace-all $tracefile
set tcpfile [open Tahoe1_[lindex $argv 1].tcp w] 
Agent/TCP set trace_all_oneline_ true

##### Setting Node
set n1 [$ns node] 
set n2 [$ns node] 
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node] 

##### Setting Link
$ns duplex-link $n1 $n2 10Mb 5ms DropTail
$ns duplex-link $n5 $n2 10Mb 5ms DropTail
$ns duplex-link $n2 $n3 10Mb 5ms DropTail
$ns duplex-link $n3 $n4 10Mb 5ms DropTail
$ns duplex-link $n3 $n6 10Mb 5ms DropTail

##### Setting Queue Length 
$ns queue-limit $n2 $n3 20

##### Setting UDP Agent
set udp [new Agent/UDP] 
$ns attach-agent $n2 $udp 
set null [new Agent/Null] 
$ns attach-agent $n3 $null 
$ns connect $udp $null 

##### Setting CBR Application
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR 
##### Setting the CBR rate
$cbr set rate_ [lindex $argv 1]mb

##### Setting TCP Agent
set tcp [new Agent/TCP]
$ns attach-agent $n1 $tcp
#$tcp set packetSize_ 900 
set sink [new Agent/TCPSink] 
$ns attach-agent $n4 $sink 
$ns connect $tcp $sink
$tcp set window_ 20

### Setting output file of TCP Agent
$tcp attach-trace $tcpfile
$tcp trace cwnd_

##### Setting FTP Application
set ftp [new Application/FTP] 
$ftp attach-agent $tcp
$ftp set type_ FTP  

##### Setting time schedule of simulation
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp start"
$ns at 10.0 "$ftp stop"
$ns at 12.0 "$cbr stop" 
$ns at 12.0 "finish" 

proc finish {} {
	global ns tracefile tcpfile 
	$ns flush-trace
	close $tracefile
    close $tcpfile
	exit 0 
}

##### Finish setting and start simulation
$ns run

