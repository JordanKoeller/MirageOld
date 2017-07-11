import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--load",nargs='?', type=str, help='Follow with a .param file to load in as parameters.')
parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')
parser.add_argument("--nogui",action='store_true',help='When specified, disables all things Qt so program can run without an event loop.')
parser.add_argument("-v","--visualize",action='store_true',help='Launch program in visualization perspective.')
parser.add_argument("-q","--queue",action='store_true',help='Launch program in experiment queue perspective.')
args = parser.parse_args()

if args.visualize:
	print("Visualizing")
if args.queue:
	print("Queue")
if args.nogui:
	print("Nogui")
if args.load:
	print(str(args.load))
if args.run:
	print(str(args.run))