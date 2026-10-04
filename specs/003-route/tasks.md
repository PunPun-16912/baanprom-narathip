# TASKS-ROUTE | v2.0 | from PLAN-ROUTE v2.0 | date: 2026-10-04

Feature: การรับงานตามเส้นทาง (ซาเล้ง)
Spec ID: SPEC-ROUTE v2.0
อ้างอิง plan.md: PLAN-ROUTE v2.0

สรุป: มี 10 task ทั้งหมด และมี 3 task ที่ต้องรอ Q-01 ก่อนเริ่มพัฒนาเต็มรูปแบบ
สรุปต่อ: การรอ Q-01 เน้นเรื่อง race condition เมื่อซาเล้งกดรับงานพร้อมกัน และผลกระทบต่อการใช้งานแบบ real-time

### T-01 ตั้งโครงข้อมูลและ Redis Geo-Index สำหรับคำขอรับซื้อขยะ
- รองรับ: REQ-FN-002, REQ-QA-002, REQ-OP-002
- ตรวจด้วย: AC-04-01, AC-04-02
- ไฟล์ที่แตะ: backend/app/db/models.py, backend/app/db/session.py, backend/app/config.py, backend/app/route/service.py
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: Redis Geo-Index และ schema ของ ScrapRequest / SalengLocation พร้อมใช้งานได้และผ่าน smoke test อย่างง่าย
- สถานะ: เสร็จ รอทีมตรวจ

### T-02 สร้าง API ค้นหางานตามรัศมี 5 กม. และคำนวณระยะทาง
- รองรับ: REQ-FN-002, REQ-OP-002, REQ-QA-002
- ตรวจด้วย: AC-04-01, AC-04-02, AC-04-03, AC-04-06
- ไฟล์ที่แตะ: backend/app/route/router.py, backend/app/route/service.py, backend/app/schemas.py
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: API คืนรายการงานที่อยู่ภายในรัศมี 5 กม. และค่าระยะทางสอดคล้องกับข้อกำหนดความคลาดเคลื่อน GPS ไม่เกิน 15%
- สถานะ: พร้อมทำ

### T-03 สร้างหน้าจอแสดงรายการงานตามเส้นทางด้วย mock API
- รองรับ: REQ-FN-002, REQ-FN-001
- ตรวจด้วย: AC-04-03, AC-04-04
- ไฟล์ที่แตะ: frontend/src/pages/RouteList.jsx, frontend/src/api/client.js, frontend/src/__tests__/AC-04-03.mock.test.jsx
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: หน้าจอแสดงประเภทขยะ ราคากลาง และระยะทางจากซาเล้งได้จาก mock API โดยไม่ต้องรอ backend จริง
- สถานะ: พร้อมทำ

### T-04 สร้างกลไก Lock และตรวจสอบ race condition เมื่อกดรับงานพร้อมกัน
- รองรับ: REQ-BR-002, Q-01
- ตรวจด้วย: AC-04-05
- ไฟล์ที่แตะ: backend/app/route/service.py, backend/app/route/router.py, backend/app/db/models.py
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: การส่งคำขอรับงานพร้อมกัน 2 request ให้ได้สิทธิ์คนเดียวตามกติกา “First-come” ที่ถึง server ก่อน
- สถานะ: รอ Q-01

### T-05 เชื่อมหน้าจอรับงานกับ API จริง
- รองรับ: REQ-BR-002, REQ-FN-002
- ตรวจด้วย: AC-04-05
- ไฟล์ที่แตะ: frontend/src/pages/RouteAccept.jsx, frontend/src/api/client.js
- ต้องทำหลัง: T-03, T-04
- เสร็จเมื่อ: ซาเล้งกดรับงานจาก UI แล้วเห็นสถานะ “มีผู้รับงานแล้ว” และได้รับผลตอบกลับที่ตรงกับ backend จริง
- สถานะ: รอ Q-01

### T-06 ปกปิดพิกัดและที่อยู่ผู้ขายจนกว่าจะมีผู้รับงานแล้ว
- รองรับ: REQ-SEC-002
- ตรวจด้วย: AC-04-08
- ไฟล์ที่แตะ: backend/app/privacy.py, backend/app/route/router.py, backend/app/route/service.py, frontend/src/pages/RouteList.jsx
- ต้องทำหลัง: T-02
- เสร็จเมื่อ: ซาเล้งก่อนรับงานเห็นเฉพาะระดับตำบล/แขวงเท่านั้น และพิกัดจริงถูกซ่อนจนกว่าสถานะเปลี่ยนเป็น “มีผู้รับงานแล้ว”
- สถานะ: พร้อมทำ

### T-07 ตรวจสอบตัวตน Thai-ID / DBD-ID ก่อนเปิดสิทธิ์รับงาน
- รองรับ: SC-04, REQ-FN-002
- ตรวจด้วย: AC-04-08
- ไฟล์ที่แตะ: backend/app/auth/verification.py, backend/app/route/service.py, backend/app/route/router.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: ซาเล้งที่ยังไม่ได้ยืนยันตัวตนถูกปฏิเสธจากการกดรับงาน และซาเล้งที่ยืนยันแล้วสามารถกดรับงานได้
- สถานะ: พร้อมทำ

### T-08 ทดสอบประสิทธิภาพและความแม่นยำของระบบค้นหา/รับงาน
- รองรับ: REQ-OP-002, REQ-QA-002
- ตรวจด้วย: AC-04-06, AC-04-07
- ไฟล์ที่แตะ: backend/tests/test_route_accuracy.py, backend/tests/test_route_performance.py
- ต้องทำหลัง: T-02
- เสร็จเมื่อ: สามารถพิสูจน์ได้ว่า response time p95 <= 3 วินาที และความคลาดเคลื่อน GPS ไม่เกิน 15% ใน dataset ที่จำลอง
- สถานะ: พร้อมทำ

### T-09 จัดการ API quota และข้อจำกัดน้ำหนักบรรทุกของซาเล้ง
- รองรับ: REQ-CON-002, REQ-CON-003
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-09
- ไฟล์ที่แตะ: backend/app/config.py, backend/app/route/service.py, backend/app/route/router.py
- ต้องทำหลัง: T-02
- เสร็จเมื่อ: ระบบมี rate limit สำหรับ Maps API และปฏิเสธงานหากน้ำหนักบรรทุกเกินข้อจำกัดที่ยานพาหนะรองรับ
- สถานะ: พร้อมทำ

### T-10 ทดสอบ concurrent load 200 คนและสรุปผล QA
- รองรับ: REQ-QA-002, REQ-BR-002
- ตรวจด้วย: AC-04-05, AC-04-07
- ไฟล์ที่แตะ: backend/tests/test_route_load.py, docs/ac-results.md
- ต้องทำหลัง: T-04, T-08
- เสร็จเมื่อ: มีผล load test สำหรับ 200 users พร้อมกันที่แสดงว่า p95 อยู่ภายใต้ 3 วินาที และ race condition ยังอยู่ในความควบคุม
- สถานะ: รอ Q-01

## ตารางตรวจความครบ (AC)
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-04-01 | T-01, T-02 |
| AC-04-02 | T-01, T-02 |
| AC-04-03 | T-02, T-03 |
| AC-04-04 | T-03 |
| AC-04-05 | T-04, T-05, T-10 |
| AC-04-06 | T-02, T-08 |
| AC-04-07 | T-08, T-10 |
| AC-04-08 | T-06, T-07 |

## ตารางตรวจความครบ (Constraint)
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| REQ-CON-002 | T-09 |
| REQ-CON-003 | T-09 |

## สิ่งที่ยังไม่ทำ
- Q-01: กรณีซาเล้ง 2 คนกดรับงานพร้อมกันในเสี้ยววินาทีเดียวกัน — task ที่รออยู่: T-04, T-05, T-10

## Note
- T-04, T-05, T-10 ถูกปักหมุดให้อยู่ในสถานะ “รอ Q-01” ตาม spec ข้อ 9 จนกว่าทีมจะตัดสินใจเรื่อง first-come policy อย่างชัดเจน
- งานที่อยู่ใน Non-goals เช่น AI คัดแยกขยะอัตโนมัติ หรือระบบโลจิสติกส์ระดับโรงงาน ถูก intentionally ไม่จัดเป็น task ตามข้อจำกัดของ spec
