$fastApiCommand = "fastapi run"
$rqWorkerCommand = "py worker.py" 

Start-Process powershell -ArgumentList "-NoExit", "-Command", $fastApiCommand

Start-Process powershell -ArgumentList "-NoExit", "-Command", $rqWorkerCommand
