// หน้าหลักของ feature UC-07: เลือกช่าง แล้วยืนยัน แล้วดูผล
// ตัวอย่างใช้ลูกค้าและที่อยู่คงที่ (การเข้าสู่ระบบ UC-10 และเลือกที่อยู่ UC-02 อยู่นอกขอบเขต feature นี้)
import { useState } from 'react'
import { api as realApi } from './api/client.js'
import TechnicianPicker from './pages/TechnicianPicker.jsx'
import ConfirmBooking from './pages/ConfirmBooking.jsx'
import BookingResult from './pages/BookingResult.jsx'
import RouteList from './pages/RouteList.jsx'

export default function App({ api = realApi, customerId = 1, addressId = 1, salengId = null }) {
  const [held, setHeld] = useState(null)
  const [job, setJob] = useState(null)
  const [feature, setFeature] = useState('booking')

  return (
    <main className="mx-auto max-w-2xl p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-teal-800">บ้านพร้อม</h1>
        <nav className="my-4 flex gap-3" aria-label="เลือกฟีเจอร์">
          <button type="button" onClick={() => setFeature('booking')} aria-pressed={feature === 'booking'}>
            จองช่าง
          </button>
          <button type="button" onClick={() => setFeature('route')} aria-pressed={feature === 'route'}>
            งานรับซื้อใกล้ฉัน
          </button>
        </nav>
      </header>
      {feature === 'route' && <RouteList api={api} salengId={salengId} />}
      {feature === 'booking' && !held && !job && (
        <TechnicianPicker api={api} customerId={customerId} addressId={addressId} onHeld={setHeld} />
      )}
      {feature === 'booking' && held && !job && (
        <ConfirmBooking api={api} customerId={customerId} addressId={addressId} held={held}
          onConfirmed={setJob}
          onPickAlternative={(a) => setHeld({ ...held, slot: a, technician: { technician_id: a.technician_id, name: a.technician_name } })} />
      )}
      {feature === 'booking' && job && <BookingResult job={job} onRestart={() => { setHeld(null); setJob(null) }} />}
    </main>
  )
}
