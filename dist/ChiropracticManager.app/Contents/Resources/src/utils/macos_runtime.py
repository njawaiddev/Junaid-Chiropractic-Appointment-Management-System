import sys
import os
import Foundation
import objc
import AppKit

def setup_macos_app():
    """Configure macOS application settings"""
    if sys.platform == "darwin":
        try:
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
            
            # Create the delegate class
            AppDelegate = objc.createClass(
                'AppDelegate',
                superclass=AppKit.NSObject,
                protocols=['NSApplicationDelegate']
            )

            # Add methods to the delegate class
            def applicationDidFinishLaunching_(self, notification):
                app = notification.object()
                app.activateIgnoringOtherApps_(True)

            def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
                return True

            AppDelegate.addMethod(b'applicationDidFinishLaunching:', applicationDidFinishLaunching_, b'v@:@')
            AppDelegate.addMethod(b'applicationShouldTerminateAfterLastWindowClosed:', applicationShouldTerminateAfterLastWindowClosed_, b'B@:@')

            # Create and set the delegate
            delegate = AppDelegate.alloc().init()
            app.setDelegate_(delegate)
            
        except Exception as e:
            print(f"Error setting up macOS application: {str(e)}", file=sys.stderr)
            raise

# Run setup when the module is imported
setup_macos_app() 