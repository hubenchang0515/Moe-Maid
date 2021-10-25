#! /usr/bin/bash

# 此脚本用于git分支合并时,比较两个分支之间的提交差异
# git cherry-pick 会生成新的提交和哈希值
# 导致比较两个分支之间不同的commit时,会包含通过cherry-pick摘取过的提交
# 此脚本根据提交的标题来比较提交是否相同,打印两个分支之间的不同提交

if [ "$#" != "2" ]
then
    echo "Usage: $0 <target-branch> <source-branch>" >> /dev/stderr
    exit 1
fi

TARGET_BRANCH=$1
SOURCE_BRANCH=$2

COMMIT_LIST=$(git log --pretty=format:"%H" ^$TARGET_BRANCH $SOURCE_BRANCH)

declare -a DIFF_COMMIT_LIST

for commit in ${COMMIT_LIST[@]}
do
    title=$(git log --pretty=format:"%s" -1 $commit)
    git log --pretty=format:"%s" $TARGET_BRANCH | grep "$title" >> /dev/null
    if [ "$?" != "0" ]
    then
        DIFF_COMMIT_LIST[${#DIFF_COMMIT_LIST[@]}]=$commit
    else
        echo "Skip same title: $title" >> /dev/stderr
    fi
done

for commit in ${DIFF_COMMIT_LIST[@]}
do
    echo $commit
done