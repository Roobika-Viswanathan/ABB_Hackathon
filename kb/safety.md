Title: Safety Interlocks

- EmergencyStop trips all actuators immediately and latches until reset.
- Motor must have permissives: Not EStop, GuardDoorClosed, NoFault, ReadyToRun.
- Start command must be edge-triggered; Stop must be level-sensitive.
- Add run-time watchdog and timeout protection around motion.
- Include manual mode bypass with explicit operator confirmation.
