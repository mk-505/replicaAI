'use client';

import { useState } from 'react';

function Spinner() {
    return (
        <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-600">Loading...</p>
        </div>
    );
}

export default function Home() {
    const [targetUrl, setTargetUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [clonedHtml, setClonedHtml] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setClonedHtml(null);

        try {
            const response = await fetch('http://localhost:8000/clone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ target_url: targetUrl }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setClonedHtml(data.cloned_html);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            console.error('Error cloning website:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-6 py-12">
                <div className="bg-white rounded-lg shadow-sm p-8 space-y-8">
                    <div className="text-center space-y-2">
                        <h1 className="text-3xl font-bold text-gray-900">Website Cloner</h1>
                        <p className="text-gray-600">Enter a URL to clone its HTML structure</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                                Website URL
                            </label>
                            <input
                                type="url"
                                id="url"
                                value={targetUrl}
                                onChange={(e) => setTargetUrl(e.target.value)}
                                placeholder="Enter website URL (e.g., https://example.com)"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                                required
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            disabled={loading}
                        >
                            {loading ? 'Cloning...' : 'Clone Website'}
                        </button>

                        {error && (
                            <div className="p-4 text-red-700 bg-red-50 rounded-lg border border-red-200">
                                {error}
                            </div>
                        )}
                    </form>

                    {loading && (
                        <div className="flex justify-center py-8">
                            <Spinner />
                        </div>
                    )}

                    {clonedHtml && (
                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold text-gray-900">Cloned Website Preview</h2>
                            <iframe
                                srcDoc={clonedHtml}
                                style={{
                                    width: "100%",
                                    height: "80vh",
                                    border: "1px solid #e5e7eb",
                                    borderRadius: "0.5rem",
                                }}
                                sandbox="allow-same-origin"
                                className="shadow-sm"
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 