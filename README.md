Robert Reid, Kiernan King

Receiver.py provided by Abraham Gale

Stop and wait is so much slower comparatively due to the main principle of the stop and wait protocol: the next data packet cannot be sent until the previous data packet sent is acknowleded. In the case of a lost packet, the sender could potentially wait indefinitely for the ACK to send the next packet, since the receiver does not ever receive a packet. 

*stop_and_wait.py with 0.5 ACK + PACK drop took 28 minutes and 9 seconds.
*Comparatively, sender.py with receiver.py variables set to 0.5 for ACK, PACK, HALF drop should take about 3 minutes and 5 seconds.

Resources referenced include:
- https://docs.python.org/3/library/select.html
- https://www.youtube.com/watch?v=2Oq4FQSr21I
- https://datatracker.ietf.org/doc/html/rfc5681
- https://datatracker.ietf.org/doc/html/rfc793#ref-3


