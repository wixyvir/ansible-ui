import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LogPage from './pages/LogPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/log/:logId" element={<LogPage />} />
        <Route path="/" element={
          <div className="min-h-screen bg-slate-900 py-6 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
              <div className="flex flex-col items-center justify-center h-64">
                <h1 className="text-2xl font-bold text-slate-100 mb-4">Ansible UI</h1>
                <p className="text-slate-400">Please navigate to /log/&lt;uuid&gt; to view a log</p>
              </div>
            </div>
          </div>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
