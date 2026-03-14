import React, { useState, useEffect } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { apiService } from '../services/api';
import type { Company } from '../types';

interface SearchProps {
  onCompanySelect: (company: Company) => void;
}

// Cache for companies list
let companiesCache: Company[] | null = null;
let cacheFetchPromise: Promise<Company[]> | null = null;

export const Search: React.FC<SearchProps> = ({ onCompanySelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const searchCompanies = async () => {
      if (query.length < 2) {
        setResults([]);
        setShowResults(false);
        return;
      }

      try {
        setLoading(true);

        // Load companies from cache or fetch once
        let companies = companiesCache;
        if (!companies) {
          if (!cacheFetchPromise) {
            cacheFetchPromise = apiService.getCompanies().then(data => {
              companiesCache = data;
              cacheFetchPromise = null;
              return data;
            });
          }
          companies = await cacheFetchPromise;
        }

        const filtered = companies.filter(
          (company) =>
            company.ticker.toLowerCase().includes(query.toLowerCase()) ||
            company.name.toLowerCase().includes(query.toLowerCase())
        );
        setResults(filtered);
        setShowResults(true);
      } catch (error) {
        console.error('Failed to search companies:', error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(searchCompanies, 300);
    return () => clearTimeout(debounceTimer);
  }, [query]);

  const handleSelect = (company: Company) => {
    onCompanySelect(company);
    setQuery('');
    setResults([]);
    setShowResults(false);
  };

  return (
    <div className="relative">
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neon-cyan w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies by ticker or name..."
          className="input w-full pl-10 pr-4 py-2"
        />
      </div>

      {showResults && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-dark-card border border-neon-cyan rounded-lg shadow-neon-cyan max-h-96 overflow-y-auto scrollbar-neon">
          {loading ? (
            <div className="p-4 text-center text-neon-cyan">
              <div className="spinner mx-auto mb-2"></div>
              <span className="text-sm">Loading...</span>
            </div>
          ) : (
            results.map((company) => (
              <div
                key={company.id}
                onClick={() => handleSelect(company)}
                className="p-3 hover:bg-neon-cyan/10 cursor-pointer border-b border-dark-border last:border-b-0 transition-colors group"
              >
                <div className="font-bold text-white group-hover:text-neon-cyan transition-colors">{company.ticker}</div>
                <div className="text-sm text-gray-500 group-hover:text-gray-400 transition-colors">{company.name}</div>
              </div>
            ))
          )}
        </div>
      )}

      {showResults && !loading && results.length === 0 && query.length >= 2 && (
        <div className="absolute z-10 w-full mt-1 bg-dark-card border border-dark-border rounded-lg shadow-lg p-4 text-center text-gray-500">
          No companies found
        </div>
      )}
    </div>
  );
};
