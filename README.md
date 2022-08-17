Robert Reid, Kiernan King

Stop and wait is so much slower comparatively due to the main principle of the stop and wait protocol: the next data packet cannot be sent until the previous data packet sent is acknowleded. In the case of a lost packet, the sender could potentially wait indefinitely for the ACK to send the next packet, since the receiver does not ever receive a packet. 

*Stop and Wait with 0.5 ACK + PACK drop took 28 minutes and 9 seconds.
*Comparatively, window slider with 0.5 ACK + PACK + HALF drop took 3 minutes and 5 seconds.

Resources referenced include:
- https://docs.python.org/3/library/select.html
- https://www.youtube.com/watch?v=2Oq4FQSr21I
- https://datatracker.ietf.org/doc/html/rfc5681
- https://datatracker.ietf.org/doc/html/rfc793#ref-3

#Receiver.py provided by Abraham Gale
