import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from '../App.jsx'

test('AC-04-03 ค้นรายการใกล้ GPS และเปิดพิกัดจริงหลังรับงานเท่านั้น', async () => {
  const api = {
    getRouteRequests: vi.fn().mockResolvedValue({
      status: 200,
      body: {
        radius_km: 5,
        items: [{
          request_id: 9,
          status: 'รอผู้รับงาน',
          area_label: 'แขวงตลาดน้อย',
          scrap_type: 'กระดาษ',
          estimated_price: 120,
          distance_km: 0.2,
        }],
      },
    }),
    acceptRouteRequest: vi.fn().mockResolvedValue({
      status: 200,
      body: {
        request_id: 9,
        status: 'มีผู้รับงานแล้ว',
        accepted_by_saleng_id: 11,
        geo_point: { lat: 13.756, lng: 100.534 },
      },
    }),
  }
  const getCurrentPosition = vi.fn((success) => success({
    coords: { latitude: 13.7563, longitude: 100.535 },
  }))
  Object.defineProperty(globalThis.navigator, 'geolocation', {
    configurable: true,
    value: { getCurrentPosition },
  })

  render(<App api={api} salengId={11} />)
  fireEvent.click(screen.getByRole('button', { name: 'งานรับซื้อใกล้ฉัน' }))
  fireEvent.click(screen.getByRole('button', { name: 'ค้นหางานจากตำแหน่ง GPS' }))

  await waitFor(() => expect(api.getRouteRequests).toHaveBeenCalledWith({
    lat: 13.7563,
    lng: 100.535,
  }))
  expect(await screen.findByText('แขวงตลาดน้อย')).toBeInTheDocument()
  expect(screen.getByText(/ราคาประเมิน: 120 บาท/)).toBeInTheDocument()
  expect(screen.getByRole('note')).toHaveTextContent('ไม่ใช่ราคากลางอ้างอิงรายวัน')
  expect(screen.queryByText(/13\.756/)).not.toBeInTheDocument()

  fireEvent.click(screen.getByRole('button', { name: 'รับงานนี้' }))
  expect(await screen.findByRole('status')).toHaveTextContent('13.756, 100.534')
  expect(api.acceptRouteRequest).toHaveBeenCalledWith({ requestId: 9, salengId: 11 })
})

test('AC-04-08 แจ้งชัดเมื่อ provider ยืนยันตัวตนยังไม่พร้อม', async () => {
  const api = {
    getRouteRequests: vi.fn().mockResolvedValue({
      status: 200,
      body: {
        radius_km: 5,
        items: [{
          request_id: 9,
          status: 'รอผู้รับงาน',
          area_label: 'แขวงตลาดน้อย',
          scrap_type: 'กระดาษ',
          estimated_price: 120,
          distance_km: 0.2,
        }],
      },
    }),
    acceptRouteRequest: vi.fn().mockResolvedValue({
      status: 503,
      body: { detail: 'ยังไม่ได้เชื่อมต่อผู้ให้บริการยืนยันตัวตน Thai-ID/DBD-ID' },
    }),
  }
  Object.defineProperty(globalThis.navigator, 'geolocation', {
    configurable: true,
    value: { getCurrentPosition: (success) => success({ coords: { latitude: 13.756, longitude: 100.534 } }) },
  })

  render(<App api={api} salengId={11} />)
  fireEvent.click(screen.getByRole('button', { name: 'งานรับซื้อใกล้ฉัน' }))
  fireEvent.click(screen.getByRole('button', { name: 'ค้นหางานจากตำแหน่ง GPS' }))
  fireEvent.click(await screen.findByRole('button', { name: 'รับงานนี้' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('ยังไม่ได้เชื่อมต่อผู้ให้บริการ')
})

test('AC-04-04 แยกราคาประเมินจากราคากลางที่ยังไม่มีแหล่งข้อมูล', async () => {
  const api = {
    getRouteRequests: vi.fn().mockResolvedValue({
      status: 200,
      body: {
        radius_km: 5,
        items: [{
          request_id: 9,
          status: 'รอผู้รับงาน',
          area_label: 'แขวงตลาดน้อย',
          scrap_type: 'กระดาษ',
          estimated_price: 120,
          distance_km: 0.2,
        }],
      },
    }),
    acceptRouteRequest: vi.fn(),
  }
  Object.defineProperty(globalThis.navigator, 'geolocation', {
    configurable: true,
    value: { getCurrentPosition: (success) => success({ coords: { latitude: 13.756, longitude: 100.534 } }) },
  })

  render(<App api={api} />)
  fireEvent.click(screen.getByRole('button', { name: 'งานรับซื้อใกล้ฉัน' }))
  fireEvent.click(screen.getByRole('button', { name: 'ค้นหางานจากตำแหน่ง GPS' }))

  expect(await screen.findByText(/ราคาประเมิน: 120 บาท/)).toBeInTheDocument()
  expect(screen.getByRole('note')).toHaveTextContent('ยังไม่มีแหล่งข้อมูลราคากลาง')
})
