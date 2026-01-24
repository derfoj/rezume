import React from 'react';
import { Skeleton } from './Skeleton';

const DashboardSkeleton = () => {
    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-500">
            {/* Navbar loading state */}
            <div className="p-6 max-w-7xl mx-auto w-full flex justify-between items-center">
                <Skeleton className="h-8 w-32" />
                <div className="flex gap-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <Skeleton className="h-10 w-24 rounded-lg" />
                </div>
            </div>

            <main className="flex flex-col items-center justify-center max-w-6xl mx-auto px-6 py-12">
                {/* Hero Skeleton */}
                <div className="mb-20 flex flex-col items-center gap-8 text-center w-full">
                    <Skeleton className="w-32 h-32 md:w-40 md:h-40 rounded-full" />
                    <div className="flex flex-col items-center gap-4 w-full max-w-2xl">
                        <Skeleton className="h-6 w-48 rounded-full" />
                        <Skeleton className="h-12 w-3/4" />
                        <Skeleton className="h-6 w-full" />
                        <Skeleton className="h-4 w-2/3" />
                    </div>
                </div>

                {/* Cards Grid Skeleton */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-7xl">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 h-[300px] flex flex-col">
                            <Skeleton className="w-12 h-12 rounded-xl mb-6" />
                            <Skeleton className="h-8 w-3/4 mb-3" />
                            <Skeleton className="h-20 w-full mb-8" />
                            <Skeleton className="h-6 w-32 mt-auto" />
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};
export default DashboardSkeleton;
