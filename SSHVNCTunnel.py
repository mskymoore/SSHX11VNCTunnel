import tkinter as tk
import subprocess as sp
import threading
import time as t
import queue as q

global root, IPEntry, target

class OutputConsole(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.text = tk.Text(self, state="disabled", width=95, undo=True)
        self.text.pack(expand=True, fill="both")
        self.ssh_tunnel = None
        self.target = ""
        self.running = False
        self.bottom = tk.Frame(self)

    def display(self, message):
        self.text.config(state="normal")
        self.text.insert(tk.END,message)
        self.text.see(tk.END)
        self.text.update_idletasks()
        self.text.config(state="disabled")

    def Launch(self, event=None):
        try:
            #Test live process output here
            #self.ssh_tunnel = sp.Popen(['./test.sh',IPEntry.get()],stdout=sp.PIPE,stderr=sp.STDOUT, bufsize=1)
            target = IPEntry.get()
            self.target = target
            if sp.run( ['ping', self.target, '-c', '1'] ).returncode == 0:
                print( 'calling on ' + target )
                self.ssh_tunnel = sp.Popen(['./ssh_vnc.sh' ,self.target],stdout=sp.PIPE,stderr=sp.STDOUT)
                iterator = iter(self.ssh_tunnel.stdout.readline, b"")

                while self.ssh_tunnel.poll() is None:
                    for line in iterator:
                        if str(line).count("The VNC desktop is"):
                            print(line.decode())
                            desktopString = line.decode().partition(": ")[2].strip()
                            t.sleep(1)
                            self.vnc_viewer = sp.Popen( ['vncviewer', desktopString] )
                            print(desktopString)
                        self.display(line.decode("utf-8"))
                self.display("Process Completed.\n")
            else:
                self.display('Please enter a valid IP Address or Hostname.\n')
                
        except FileNotFoundError:
            self.display("Unknown command\n")
        except IndexError:
            self.display("Error\n")
        self.Kill()

    def threadProcess(self):
        while self.running:
            self.Launch()

    def Thread(self, event=None):
        self.Kill()
        self.running = True
        threading.Thread( target=self.threadProcess ).start()

    def Kill(self):
        if self.ssh_tunnel:
            print( "Attempting to kill " + str( self.ssh_tunnel ) + "\n" )
            try:
                self.ssh_tunnel.kill()
            except ProcessLookupError:
                pass
            try:
                self.display( sp.run( ['./ssh_kill_vnc.sh', self.target], stdout=sp.PIPE, stderr=sp.STDOUT ).stdout.decode() )
            except Exception:
                pass

        self.running = False

root = tk.Tk()
topWidgetW = 350
topWidgetH = 100
rootW = topWidgetW*2
rootH = 550
root.minsize( width=rootW, height=rootH )
root.maxsize( width=rootW, height=rootH )
root.title( 'Remote Launcher' )
bitImage = tk.PhotoImage( file='S2.png' )
root.tk.call( 'wm', 'iconphoto', root._w, bitImage )
    
Output = tk.LabelFrame( root, labelanchor='n', text='Output', width=rootW, height=topWidgetW+50 )
Output.grid_propagate(False)
Output.grid( row=1, column=0, columnspan=2 )

outputText = OutputConsole(root)
outputText.place( in_=Output, relx=0.02 )
    
LaunchParams = tk.LabelFrame( root, labelanchor='n', text='Launch Parameters', width=topWidgetW, height=topWidgetH )
LaunchParams.grid_propagate(False)
LaunchParams.grid( row=0, column=0 )
        
IPorHostNameLabel = tk.Label( root, text='IP Address or Hostname:' )
IPorHostNameLabel.place( in_=LaunchParams, rely=0.01 )

IPEntry = tk.Entry( root, text='Enter Ip address here.', width=25 )
IPEntry.bind( '<Key-Return>', outputText.Thread )
IPEntry.place( in_=LaunchParams, relx=.05, rely=0.3 )

Controls = tk.LabelFrame( root, labelanchor='n', text='Controls', width=topWidgetW, height=topWidgetH )
Controls.grid_propagate(False)
Controls.grid( row=0, column=1 )

launchButton = tk.Button( root, text='Launch!', bg='#33AA33', fg='#FFFFFF', command=lambda: outputText.Thread() )
launchButton.place( in_=Controls, relx=0.2, rely=0.2 )

killButton = tk.Button( root, text='Kill!', bg='#AA3333', fg='#FFFFFF', command=lambda: outputText.Kill() )
killButton.place( in_=Controls, relx=0.5, rely=0.2 )

if __name__ == "__main__":
    root.mainloop()


