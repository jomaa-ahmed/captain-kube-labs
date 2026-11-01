#!/bin/bash
got=$(tr -d '[:space:]' < /root/shop-fqdn.txt 2>/dev/null); got=${got%.}
[ "$got" = "shop.market.svc.cluster.local" ] || exit 1
