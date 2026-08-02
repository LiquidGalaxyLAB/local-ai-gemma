# Slave Solo KML Refresh Fix

## The Problem

Slave VMs (lg2, lg3) have a "Solo KML" NetworkLink in their
`~/earth/kml/slave/myplaces.kml` that loads `slave_2.kml` / `slave_3.kml`
respectively. By default this link has **no refreshInterval** — the slave
loads the KML once at Earth startup and never re-polls. Changes to
`/var/www/html/kml/slave_3.kml` are invisible until the next Earth restart.

## The Filename Mismatch

The existing `lg-refresh-set` helper targets `slave_x.kml` (the PHP-resolved
variable form that appears in the **master's** slave myplaces.kml). But
**each slave's actual Solo KML uses its own specific filename:**

| Frame | Solo KML filename |
|-------|-------------------|
| lg2   | `slave_2.kml`     |
| lg3   | `slave_3.kml`     |

This means `lg-refresh-set` won't match — it searches for `slave_x.kml`
which doesn't exist in the slaves' files.

## The Fix

Add `<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>`
to each slave's Solo KML `<Link>` via sed, by reaching through lg1:

```bash
# On lg1, for each slave:
sshpass -p 'lg' ssh lg@lg2 "sed -i '/slave_2.kml<\\/href>/a\\ <refreshMode>onInterval</refreshMode>\\n <refreshInterval>3</refreshInterval>' ~/earth/kml/slave/myplaces.kml"
sshpass -p 'lg' ssh lg@lg3 "sed -i '/slave_3.kml<\\/href>/a\\ <refreshMode>onInterval</refreshMode>\\n <refreshInterval>3</refreshInterval>' ~/earth/kml/slave/myplaces.kml"
```

Then **restart Earth once** (`lg-relaunch-direct` or manual launch per the display-owning user) so the new myplaces.kml takes effect. After that, any write to `slave_2.kml` (rightmost = floor(N/2)+1 → lg2 for N=3) auto-appears on the rightmost screen within 3 seconds. **Note: also verify `##LG_PHPIFACE##` is resolved to `http://lg1:81/` in the runtime myplaces — an unresolved placeholder means Earth never polls.**

## Verification

```bash
# Check each slave
sshpass -p 'lg' ssh lg@lg2 "grep -A6 'Solo KML' ~/earth/kml/slave/myplaces.kml | head -8"
sshpass -p 'lg' ssh lg@lg3 "grep -A6 'Solo KML' ~/earth/kml/slave/myplaces.kml | head -8"
```

Expected output — each shows `<refreshMode>` and `<refreshInterval>` inside
the `<Link>` block:

```
<name>Solo KML</name>
<Link>
    <href>##LG_PHPIFACE##kml/slave_3.kml</href>
    <refreshMode>onInterval</refreshMode>
    <refreshInterval>3</refreshInterval>
</Link>
```

## Prerequisite: SSH Access to Slaves

The fix requires lg1 to reach lg2/lg3 via `sshpass`. Verify before starting:

```bash
sshpass -p 'lg' ssh lg@<LG-IP> \
  'sshpass -p lg ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no lg@lg3 "hostname"'
```

If this fails, the slave VMs may be on a different internal network
(e.g. 10.42.42.x NAT) not reachable from lg1's main interface. Check
`/etc/hosts` on lg1 for the correct internal IPs.
