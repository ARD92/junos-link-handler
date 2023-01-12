# junos-link-handler
An event script to handle link failures and enabling link on a redundant device.

## Topology considered
```
  192.167.1.3                192.167.1.4
+----------+                +----------+
|          |                |          |
|   vmx3   |                |   vmx4   |
|          +----------------+          |
|          |                |          |
+----+-----+                +-----+----+
     |                            |
     | ge-0/0/0                   |ge-0/0/1
     |                            |
     |                            |
     |                            |
```

The event script would run on vmx3. It would monitor for link failures on south bound interface `ge-0/0/0`. In an event the link is down (admin/oper), the script would add an admin disable knob on the interface and log into vMX4 to delete the disable knob on interface ge-0/0/1. Similarly the script could run on vMX4 to do the same task to ease up operationalizatioin

## Configure junos to identify link does
```
root@vmx3# show event-options
policy LINK-CHECK {
    events snmp_trap_link_down;
    attributes-match {
        snmp_trap_link_down.interface-name matches ge-0/0/0;
    }
    then {
        event-script linkhandle.py {
            arguments {
                peer 192.167.1.4;
                peerintf ge-0/0/1;
                lclintf ge-0/0/0;
            }
        }
    }
}
event-script {
    file linkhandle.py;
}
``` 

## Copy the script to Junos
copy the script `linkhandle.py` under `/var/db/scripts/event`

## Validate

verify if the log is written 
```
show log escript.log 
```
1. Link ge-0/0/0 goes down on vMX3 
```
root@vmx3# run show log messages | match SNMP
Jan 11 18:21:20  vmx3 mib2d[11264]: SNMP_TRAP_LINK_DOWN: ifIndex 527, ifAdminStatus down(2), ifOperStatus down(2), ifName ge-0/0/0
```

2. Event script triggered based on above log 
```
*** escript.log ***
Jan 11 20:59:29 event script processing begins
Jan 11 20:59:29 running event script 'linkhandle.py'
Jan 11 20:59:29 opening event script '/var/db/scripts/event/linkhandle.py'
Jan 11 20:59:29 reading event script 'linkhandle.py'

Jan 11 20:59:37 event script execution successful for 'linkhandle.py' with return: 0
Jan 11 20:59:37 finished event script 'linkhandle.py'
Jan 11 20:59:37 event script processing ends
```

3. Event script marks admin disable on the link ge-0/0/0 belonging to local node (vmx3)

```
[edit interfaces]
+   ge-0/0/0 {
+       disable;
+   }

Jan 11 20:59:31  vmx3 mgd[56789]: UI_COMMIT: User 'root' requested 'commit' operation (comment: none)
```

4. vMX3 programs vMX4 to remove link disable knob 
```
root@vmx4# show | compare rollback 1
[edit interfaces ge-0/0/1]
-   disable;


root@vmx4# run show log messages | match UI_COMMIT | last
Jan 11 21:04:13  vmx4 mgd[65762]: UI_COMMIT_PROGRESS: Commit operation in progress: commit complete
Jan 11 21:04:13  vmx4 mgd[65762]: UI_COMMIT_COMPLETED:  : commit complete
```
