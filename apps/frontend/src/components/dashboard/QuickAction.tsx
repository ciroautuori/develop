import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/utils/cn';

interface QuickActionProps {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick: () => void;
  variant?: 'default' | 'primary' | 'secondary' | 'destructive';
  className?: string;
}

export const QuickAction: React.FC<QuickActionProps> = ({
  title,
  description,
  icon: Icon,
  onClick,
  variant = 'default',
  className
}) => {
  return (
    <Card 
      className={cn(
        "cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-[1.02]", 
        className
      )} 
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-2 rounded-lg",
            variant === 'primary' && "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400",
            variant === 'secondary' && "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400",
            variant === 'destructive' && "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400",
            variant === 'default' && "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
          )}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-sm">{title}</CardTitle>
            <CardDescription className="text-xs">{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
    </Card>
  );
};
