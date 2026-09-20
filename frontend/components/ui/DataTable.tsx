import React from 'react';
import { cn } from '../../lib/utils';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
  keyExtractor: (item: T, index: number) => string;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  emptyMessage = 'No data records available.',
  keyExtractor,
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn('overflow-x-auto rounded-xl border border-border bg-surface/70', className)}>
      <table className="w-full text-left text-xs border-collapse">
        <thead className="bg-slate-900/80 border-b border-border text-slate-400 font-mono">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn(
                  'px-4 py-3 font-semibold uppercase tracking-wider',
                  col.align === 'right' && 'text-right',
                  col.align === 'center' && 'text-center',
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 text-slate-300">
          {data.length > 0 ? (
            data.map((item, idx) => (
              <tr key={keyExtractor(item, idx)} className="hover:bg-slate-800/40 transition-colors">
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn(
                      'px-4 py-3 whitespace-nowrap',
                      col.align === 'right' && 'text-right font-mono',
                      col.align === 'center' && 'text-center',
                      col.className
                    )}
                  >
                    {col.render ? col.render(item) : (item as Record<string, unknown>)[col.key]?.toString()}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500 font-mono">
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
