from signal import Signals
from sys import exit

def handle_signal(signal, frame) -> None:
	"""
	Handling incoming signals during runtime.
	The application is going to terminate by 0.

	signal:
	-	signal number
	frame:
	-	memory location of the occurred signal
	"""
	summary = f"""
	incoming signal number: {signal}
	type: {Signals(signal)}
	location: {frame}
	"""
	print(summary)

	exit(0)
#end function