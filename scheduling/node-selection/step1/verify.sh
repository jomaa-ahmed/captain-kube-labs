#!/bin/bash
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.disk}')" = "ssd" ] || exit 1
            [ "$(kubectl get pod fastlane -o jsonpath='{.spec.nodeSelector.disk}')" = "ssd" ] || exit 1
            [ "$(kubectl get pod fastlane -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod fastlane -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
