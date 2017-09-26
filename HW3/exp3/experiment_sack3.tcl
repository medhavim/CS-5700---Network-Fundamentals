set ns [new Simulator]

##### Setting output file
set tracefile [open Sack1_[lindex $argv 1]_[lindex $argv 2].tr w]
$ns trace-all $tracefile

### Set Output TCP File
set tcpfile [open Sack1_[lindex $argv 1]_[lindex $argv 2].tcp w]
Agent/TCP/Reno set trace_all_oneline_ true

##### Setting Node
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

##### Setting Link
$ns duplex-link $n1 $n2 10Mb 10ms [lindex $argv 1]
$ns duplex-link $n5 $n2 10Mb 10ms [lindex $argv 1]
$ns duplex-link $n2 $n3 10Mb 10ms [lindex $argv 1]
$ns duplex-link $n3 $n4 10Mb 10ms [lindex $argv 1]
$ns duplex-link $n3 $n6 10Mb 10ms [lindex $argv 1]

##### Setting Queue Length
$ns queue-limit $n1 $n2 20
$ns queue-limit $n5 $n2 20
$ns queue-limit $n2 $n3 20
$ns queue-limit $n3 $n4 20
$ns queue-limit $n3 $n6 20

##### Setting UDP Agent
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null

##### Setting CBR Application
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set rate_ 10Mb


##### Setting TCP Agent
set tcp [new Agent/TCP/Sack1]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink

##### Setting FTP Application
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

### Setting output file of TCP Agent
$tcp attach-trace $tcpfile
$tcp trace cwnd_
##### Setting the window sizes
$tcp set maxcwnd_ 200
$tcp set window_ 150

##### Setting time schedule of simulation
$ns at 1.0 "$ftp start"
$ns at 12.0 "$cbr start"
$ns at [lindex $argv 2] "$ftp stop"
$ns at 40.0 "$cbr stop"
$ns at 45.0 "finish"

proc finish {} {
        global ns tracefile tcpfile
        $ns flush-trace
        close $tracefile
        close $tcpfile
        exit 0
}

##### Finish setting and start simulation
$ns run

