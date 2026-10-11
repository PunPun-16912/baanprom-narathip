import { useState } from 'react'
import RouteAccept from './RouteAccept.jsx'

export default function RouteList({ api, salengId = null }) {
  const [items, setItems] = useState([])
  const [searching, setSearching] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')

  async function searchNearby() {
    setError('')
    setSearching(true)
    setSearched(false)
    try {
      if (!navigator.geolocation) {
        throw new Error('อุปกรณ์นี้ไม่รองรับการอ่านตำแหน่ง GPS')
      }
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
        })
      })
      const result = await api.getRouteRequests({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      })
      if (result.status < 200 || result.status >= 300) {
        throw new Error(result.body.detail || 'ค้นหาคำขอไม่สำเร็จ')
      }
      setItems(result.body.items)
      setSearched(true)
    } catch (cause) {
      setError(cause.message || 'อ่านตำแหน่งหรือค้นหาคำขอไม่สำเร็จ')
    } finally {
      setSearching(false)
    }
  }

  return (
    <section aria-labelledby="route-heading">
      <h2 id="route-heading" className="text-xl font-semibold">งานรับซื้อใกล้ฉัน</h2>
      <p>ค้นหาคำขอในรัศมีไม่เกิน 5 กม. ระบบไม่เปิดเผยพิกัดจริงก่อนรับงาน</p>
      <p role="note">
        ราคาที่แสดงเป็นราคาประเมินจากคำขอ ไม่ใช่ราคากลางอ้างอิงรายวัน
        (ยังไม่มีแหล่งข้อมูลราคากลาง)
      </p>
      <button type="button" onClick={searchNearby} disabled={searching}>
        {searching ? 'กำลังค้นหา…' : 'ค้นหางานจากตำแหน่ง GPS'}
      </button>
      {error && <p role="alert">{error}</p>}
      {searched && items.length === 0 && <p>ไม่พบคำขอในรัศมี 5 กม.</p>}
      <ul aria-label="รายการคำขอรับซื้อ">
        {items.map((item) => (
          <li key={item.request_id} className="my-3 rounded border p-4">
            <h3 className="font-semibold">{item.scrap_type}</h3>
            <p>พื้นที่: {item.area_label || 'ไม่ระบุพื้นที่'}</p>
            <p>ระยะทาง: {item.distance_km} กม.</p>
            <p>ราคาประเมิน: {item.estimated_price} บาท</p>
            <RouteAccept api={api} request={item} salengId={salengId} />
          </li>
        ))}
      </ul>
    </section>
  )
}
