cmd="python3 ."

source ./venv/bin/activate
last_pid=$(ps aux|grep "$cmd"|tr -s '[:blank:]'|cut -f 2 -d ' '|head -n 1)
kill -9 $last_pid
clear
echo -e "\n****** process id $last_pid Begin ******\n" >> nohup.out.old 
cat nohup.out >> nohup.out.old
echo -e "\n****** process id $last_pid End ******\n" >> nohup.out.old 
rm nohup.out
echo -e "\nstopped pid: $last_pid\n"
nohup $cmd &
echo "started process"
