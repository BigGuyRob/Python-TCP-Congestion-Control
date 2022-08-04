# cs352project2

https://www.youtube.com/watch?v=2Oq4FQSr21I

0. Please write down the full names and netids of both your team members.
rlr151 - Robert Reid, ktk43 - Kiernan King

1. Are there known issues or functions that aren't working currently in your attached code? If so, explain. (note that you will get half credit for any reasonably sized bug that is fully explained in the readme)
No known issues or functions that aren't working currently in the attached code.

3. What problems did you face developing code for this project? Around how long did you spend on this project (This helps me decide what I need to explain more clearly for the next projects)
A total effort of about 35 hours went into this project cumulatively between both teammates. 
There were many problems faced, including:
- Incorrect receiver.py code in dealing with the last packet being dropped.
- Sometimes, in the case of a dropped half-packet, sometimes a whole packet was being resent instead of the bit where it dropped.

4. Why is stop and wait much slower
Stop and wait is so much slower comparatively due to the main principle of the stop and wait protocol: the next data packet cannot be sent until the previous data packet sent is acknowleded. In the case of a lost packet, the sender could potentially wait indefinitely for the ACK to send the next packet, since the receiver does not ever receive a packet. 

*Stop and Wait with 0.5 ACK + PACK drop took 28 minutes and 9 seconds.
*Comparatively, window slider with 0.5 ACK + PACK + HALF drop took 3 minutes and 5 seconds.

