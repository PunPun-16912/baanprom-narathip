import { useState } from 'react'

export default function RouteAccept({ api, request, salengId }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [accepted, setAccepted] = useState(null)

  async function accept() {
    setBusy(true)
    setError('')
    try {
      const result = await api.acceptRouteRequest({
        requestId: request.request_id,
        salengId,
      })
      if (result.status < 200 || result.status >= 300) {
        throw new Error(result.body.detail || 'รับงานไม่สำเร็จ')
      }
      setAccepted(result.body)
    } catch (cause) {
      setError(cause.message || 'รับงานไม่สำเร็จ')
    } finally {
      setBusy(false)
    }
  }

  if (accepted) {
    return (
      <p role="status">
        รับงานแล้ว — พิกัด: {accepted.geo_point.lat}, {accepted.geo_point.lng}
      </p>
    )
  }

  return (
    <>
      <button type="button" onClick={accept} disabled={busy || !salengId}>
        {busy ? 'กำลังรับงาน…' : 'รับงานนี้'}
      </button>
      {!salengId && <p>ยังไม่มีบัญชีซาเล้งที่ยืนยันตัวตนสำหรับรับงาน</p>}
      {error && <p role="alert">{error}</p>}
    </>
  )
}
