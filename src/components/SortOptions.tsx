import React from 'react';
import { Vehicle } from '@/types';

interface SortOptionsProps {
  onSort: (vehicles: Vehicle[]) => void;
  vehicles: Vehicle[];
}

type SortOption = {
  label: string;
  sortFn: (a: Vehicle, b: Vehicle) => number;
};

const SortOptions: React.FC<SortOptionsProps> = ({ onSort, vehicles }) => {
  const sortOptions: Record<string, SortOption> = {
    priceLowToHigh: {
      label: 'Price: Low to High',
      sortFn: (a, b) => a.price - b.price,
    },
    priceHighToLow: {
      label: 'Price: High to Low',
      sortFn: (a, b) => b.price - a.price,
    },
    yearNewestFirst: {
      label: 'Year: Newest First',
      sortFn: (a, b) => b.year - a.year,
    },
    yearOldestFirst: {
      label: 'Year: Oldest First',
      sortFn: (a, b) => a.year - b.year,
    },
    mileageLowToHigh: {
      label: 'Mileage: Low to High',
      sortFn: (a, b) => a.mileage - b.mileage,
    },
    alphabetical: {
      label: 'Name: A to Z',
      sortFn: (a, b) => `${a.make} ${a.model}`.localeCompare(`${b.make} ${b.model}`),
    },
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const sortKey = e.target.value;
    if (sortKey && sortOptions[sortKey]) {
      const sortedVehicles = [...vehicles].sort(sortOptions[sortKey].sortFn);
      onSort(sortedVehicles);
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="sort-select" className="text-sm font-medium text-gray-700">
        Sort by:
      </label>
      <select
        id="sort-select"
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        onChange={handleSortChange}
        defaultValue=""
      >
        <option value="" disabled>
          Select option
        </option>
        {Object.entries(sortOptions).map(([key, option]) => (
          <option key={key} value={key}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SortOptions;
