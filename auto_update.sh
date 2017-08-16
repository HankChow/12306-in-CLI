#!/bin/zsh
old_list=`ls | grep station`
python3 train.py -u
new_list=`ls | grep station`
if [ $old_list != $new_list ]
then
    git rm $old_list
    git add $new_list
    git commit -m UPDATED_AUTOMATICALLY
    git push origin master
fi
