import sys
import os

def setup_macos_app():
    """Configure macOS application settings"""
    if sys.platform == "darwin":
        try:
            # Import macOS specific modules
            import Foundation
            import AppKit
            import objc
            
            # Get the main bundle
            bundle = Foundation.NSBundle.mainBundle()
            
            # Set up Info.plist keys
            info = bundle.infoDictionary()
            if info:
                # Enable high-resolution display
                info['NSHighResolutionCapable'] = True
                
                # Ensure dock icon is shown
                info['LSUIElement'] = False
                
                # Set application name
                info['CFBundleName'] = 'ChiropracticManager'
                
                # Set application category
                info['LSApplicationCategoryType'] = 'public.app-category.medical'
            
            # Configure process name
            import ctypes
            ctypes.CDLL(None).CGSSetDenyWindowServerConnections(False)
            
            # Ensure the application appears in the dock
            app = AppKit.NSApplication.sharedApplication()
            app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
            
            # Set up application delegate to handle activation
            AppDelegate = objc.generateObjCClass(
                'AppDelegate',
                superclass=Foundation.NSObject,
                protocols=['NSApplicationDelegate']
            )
            
            def applicationDidFinishLaunching_(self, notification):
                app = notification.object()
                app.activateIgnoringOtherApps_(True)
            
            def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
                return True
            
            AppDelegate.instanceMethods = {
                'applicationDidFinishLaunching:': applicationDidFinishLaunching_,
                'applicationShouldTerminateAfterLastWindowClosed:': applicationShouldTerminateAfterLastWindowClosed_
            }
            
            # Set the delegate
            delegate = AppDelegate.alloc().init()
            app.setDelegate_(delegate)
            
        except Exception as e:
            print(f"Error setting up macOS application: {str(e)}")
            import traceback
            traceback.print_exc()

# Run setup when the module is imported
setup_macos_app() 