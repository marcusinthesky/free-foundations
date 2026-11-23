import UntrustedSupport
example : ExternalSupport.unsupportedNumber = ExternalSupport.unsupportedNumber := rfl
example (_unused : ExternalSupport.unsupportedNumber = 0) : True := True.intro
