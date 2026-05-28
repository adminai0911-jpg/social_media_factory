$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument '"C:\Users\drsau\.gemini\antigravity-ide\scratch\social_media_factory\run_factory.vbs"'
$trigger1 = New-ScheduledTaskTrigger -Daily -At 9:00AM
$trigger2 = New-ScheduledTaskTrigger -Daily -At 2:00PM
$trigger3 = New-ScheduledTaskTrigger -Daily -At 8:00PM
Register-ScheduledTask -Action $action -Trigger $trigger1,$trigger2,$trigger3 -TaskName "SocialMediaFactory" -Description "Autonomous Video Generation" -Force
