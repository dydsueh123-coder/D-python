import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/common/AppLayout'
import ProtectedRoute from './components/common/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import SurveyListPage from './pages/SurveyListPage'
import SurveyResponsePage from './pages/SurveyResponsePage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/surveys" replace />} />
          <Route path="surveys" element={<SurveyListPage />} />
          <Route path="surveys/:id/respond" element={<SurveyResponsePage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
