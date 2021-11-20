#!/bin/bash -i

shopt -s expand_aliases

source $HOME/.profile
source $HOME/.bash_profile


tout=$(cd $HOME/massa/massa-client/; ./massa-client wallet_info; cd)

Address=$(echo "$tout" | grep "Address" | awk -F " " {'print $2'})
FinalBalance=$(echo "$tout" | grep "Final balance" | awk -F " " {'print $3'})
CandidateBalance=$(echo "$tout" | grep "Candidate balance" | awk -F " " {'print $3'})
LockedBalance=$(echo "$tout" | grep "Locked balance" | awk -F " " {'print $3'})
nActiveRolls=$(echo "$tout" | grep "Active rolls" | awk -F " " {'print $3'})
nFinalRolls=$(echo "$tout" | grep "Final rolls" | awk -F " " {'print $3'})
nCandidateRolls=$(echo "$tout" | grep "Candidate rolls" | awk -F " " {'print $3'})

echo "Address:$Address"
echo "Final Balance:$FinalBalance"
echo "Candidate Balance:$CandidateBalance"
echo "Locked Balance:$LockedBalance"
echo "Active Rolls:$nActiveRolls"
echo "Final Rolls:$nFinalRolls"
echo "Candidate Rolls:$nCandidateRolls"

tout=$(cd $HOME/massa/massa-client/; ./massa-client get_addresses $Address; cd)

echo "Cycles:"
echo "$(echo "$tout" | grep 'produced')"
