//
//  AppDelegate.h
//  KidsBerry
//
//  Created by Loredana Albulescu on 11/23/13.
//  Copyright (c) 2013 Loredana Albulescu. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "HelloViewController.h"

@interface AppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;
@property (strong, nonatomic) HelloViewController *mainViewController;
@property (strong, nonatomic) UINavigationController* navController;

@end
