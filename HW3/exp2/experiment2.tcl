##### Declare Simulator
set ns [new Simulator]

##### Setting output file
set tracefile [open [lindex $argv 1][lindex $argv 2]_[lindex $argv 3].tr w]
$ns trace-all $tracefile
set tcp1file [open [lindex $argv 1]_[lindex $argv 3].tcp w] 
Agent/TCP/[lindex $argv 1] set trace_all_oneline_ true
set tcp2file [open [lindex $argv 2]_[lindex $argv 3].tcp w] 
Agent/TCP/[lindex $argv 2] set trace_all_oneline_ true

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
##### Set CBR Flow rate
$cbr set rate_ [lindex $argv 3]mb

##### Setting TCP Agent1
set tcp1 [new Agent/TCP/[lindex $argv 1]]
$ns attach-agent $n1 $tcp1 
set sink1 [new Agent/TCPSink] 
$ns attach-agent $n4 $sink1 
$ns connect $tcp1 $sink1

##### Setting TCP Agent2
set tcp2 [new Agent/TCP/[lindex $argv 2]]
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2

### Setting output file of TCP Agent
$tcp1 attach-trace $tcp1file
$tcp2 attach-trace $tcp2file
$tcp1 trace cwnd_
$tcp2 trace cwnd_

##### Setting FTP Application
set ftp1 [new Application/FTP] 
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

set ftp2 [new Application/FTP] 
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP

##### Setting time schedule of simulation
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp1 start"
$ns at 1.0 "$ftp2 start"
$ns at 10.0 "$ftp2 stop"
$ns at 10.0 "$ftp1 stop"
$ns at 12.0 "$cbr stop" 
$ns at 12.0 "finish" 

proc finish {} {
	global ns tracefile tcp1file tcp2file
	$ns flush-trace
	close $tracefile
    close $tcp1file
    close $tcp2file
	exit 0 
}

##### Finish setting and start simulation
$ns run

