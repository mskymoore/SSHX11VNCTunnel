import tkinter as tk
import subprocess as sp
import threading
import time as t
import socket as s
import queue as q

global root, IPEntry, target

def ValidIP(IP):
    IPv4 = False
    IPv6 = False
    try:
        s.inet_pton(s.AF_INET,IP)
        IPv4 = True
        print("Found IPv4 Address: " + IP)
    except OSError:
        print(IP + " is not an IPv4 Address.")
        pass
    try:
        s.inet_pton(s.AF_INET6,IP)
        IPv6 = True
        print("Found IPv6 Address: " + IP)
    except OSError:
        print(IP + " is not an IPv6 Address.")
        pass
    if(IPv4 and IPv6):
        return False
    elif(IPv4 or IPv6):
        return True
    else:
        return False

def Pingable(target):
    if sp.run( ['ping', target, '-c', '1', '-W', '1'] ).returncode == 0:
        return True
    return False

#Unused at this time.
def CheckHost(target):
    if( ValidIP(target) ):
        if( Pingable(target) ):
            return True
    return False
    


class OutputConsole(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.text = tk.Text(self, state="disabled", width=95, undo=True, bg="#000000", fg="#00DD22")
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
            if ValidIP(self.target):
                if Pingable(self.target):
                    print( 'Calling on ' + self.target )
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
                    self.display('Host unreachable.\n')
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

    def Kill(self, event=None):
        if self.ssh_tunnel:
            print( "Attempting to kill " + str( self.ssh_tunnel ) + "\n" )
            try:
                self.ssh_tunnel.kill()
            except ProcessLookupError:
                pass
            try:
                if ValidIP(self.target):
                    if Pingable(self.target):
                        self.display( sp.run( ['./ssh_kill_vnc.sh', self.target], stdout=sp.PIPE, stderr=sp.STDOUT ).stdout.decode() )
            except Exception:
                pass

        self.running = False

root = tk.Tk()
topWidgetW = 350
topWidgetH = 70
rootW = topWidgetW*2
rootH = 480
root.minsize( width=rootW, height=rootH )
root.maxsize( width=rootW, height=rootH )
root.title( 'SSH Tunneled X11 VNC Launcher' )
bitImage = tk.PhotoImage( file='S2.png' )
root.tk.call( 'wm', 'iconphoto', root._w, bitImage )
    
Output = tk.LabelFrame( root, labelanchor='n', text='Output', width=rootW, height=topWidgetW+50 )
Output.grid_propagate(False)
Output.grid( row=1, column=0, columnspan=2 )

outputText = OutputConsole(root)
outputText.place( in_=Output, relx=0.02 )

root.bind("<Key-Escape>", outputText.Kill)
    
LaunchParams = tk.LabelFrame( root, labelanchor='n', text='Launch Parameters', width=topWidgetW, height=topWidgetH )
LaunchParams.grid_propagate(False)
LaunchParams.grid( row=0, column=0 )
        
IPorHostNameLabel = tk.Label( root, text='IP Address or Hostname:' )
IPorHostNameLabel.place( in_=LaunchParams, relx=0.05, rely=0.01 )

IPEntry = tk.Entry( root, text='Enter Ip address here.', width=25 )
IPEntry.bind( '<Key-Return>', outputText.Thread )
IPEntry.place( in_=LaunchParams, relx=.05, rely=0.4 )

ProcessControls = tk.LabelFrame( root, labelanchor='n', text='Process Controls', width=topWidgetW, height=topWidgetH )
ProcessControls.grid_propagate(False)
ProcessControls.grid( row=0, column=1 )

launchButton = tk.Button( root, text='Launch!', bg='#33AA33', fg='#FFFFFF', command=lambda: outputText.Thread() )
launchButton.place( in_=ProcessControls, relx=0.3, rely=0.15 )

killButton = tk.Button( root, text='Kill!', bg='#AA3333', fg='#FFFFFF', command=lambda: outputText.Kill() )
killButton.place( in_=ProcessControls, relx=0.55, rely=0.15 )

if __name__ == "__main__":
    root.mainloop()


