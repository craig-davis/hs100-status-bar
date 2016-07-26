import rumps

class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("AC Control", title=None, icon="icon.png")
        self.menu = ["AC On"]

    @rumps.clicked("AC On")
    def onoff(self, sender):
        sender.state = not sender.state

if __name__ == "__main__":
    AwesomeStatusBarApp().run()
