# simple Dialog class extension to allow for defining field length
# borrowed from https://groups.google.com/forum/#!msg/psychopy-users/hbcWbcOZx-Y/3vvUlLE3XdgJ
# made to inherit from original psychopy Dialog component

from psychopy import gui
import wx

class NewDlg( gui.Dlg ):

    def addField(self, label='', initial='', color='', choices=None, tip='',multiLineText=False,lines = 1,width =None):
        """
        Adds a (labelled) input field to the dialogue box, optional text color
        and tooltip. Returns a handle to the field (but not to the label).
        If choices is a list or tuple, it will create a dropdown selector.
        """
        self.inputFieldNames.append(label)
        if choices:
            self.inputFieldTypes.append(str)
        else:
            self.inputFieldTypes.append(type(initial))
        #if type(initial)==numpy.ndarray:
        #    initial=initial.tolist() #convert numpy arrays to lists
        if multiLineText:
            container=wx.FlexGridSizer(cols=1, vgap=0,hgap=10)
            labelAlignment = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        else:
            container=wx.FlexGridSizer(cols=2, hgap=10)
            labelAlignment = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        #create label
        labelLength = wx.Size(9*len(label)+16,25)#was 8*until v0.91.4
        inputLabel = wx.StaticText(self,-1,label,
                                        size=labelLength,
                                        style=labelAlignment)
        if len(color): inputLabel.SetForegroundColour(color)
        container.Add(inputLabel, 0,labelAlignment )
        
        inputAlignment = wx.ALIGN_CENTER_VERTICAL
        #create input control
        if type(initial)==bool:
            inputBox = wx.CheckBox(self, -1)
            inputBox.SetValue(initial)
        elif not choices:
            styleValue = 0
            if multiLineText:
                styleValue = wx.TE_MULTILINE
                inputAlignment = wx.ALIGN_TOP
            else:
                lines = 1
            if width:
                inputLength = wx.Size(9*width +16, 25*lines)
            else:
                inputLength = wx.Size(max(50, 5*len(unicode(initial))+16), 25*lines)
            inputBox = wx.TextCtrl(self,-1,unicode(initial),size=inputLength,style=styleValue)
        else:
            inputBox = wx.Choice(self, -1, choices=[str(option) for option in list(choices)])
            # Somewhat dirty hack that allows us to treat the choice just like
            # an input box when retrieving the data
            inputBox.GetValue = inputBox.GetStringSelection
            initial = choices.index(initial) if initial in choices else 0
            inputBox.SetSelection(initial)
        if len(color): inputBox.SetForegroundColour(color)
        if len(tip): inputBox.SetToolTip(wx.ToolTip(tip))

        container.Add(inputBox,0, inputAlignment,wx.LEFT|wx.RIGHT,5)
        self.sizer.Add(container, 0, wx.ALIGN_CENTER)

        self.inputFields.append(inputBox)#store this to get data back on OK
        return inputBox
