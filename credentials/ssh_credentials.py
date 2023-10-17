import pexpect

ssh = pexpect.spawn('ssh deaise@de-edu-etl.chronosavant.ru')
if ssh.expect('[Pp]assword') == 0:
    try:
        ssh.sendline('meriadocbrandybuck')
        print('ssh connection established')
    except BaseException:
        print('check the connection')



