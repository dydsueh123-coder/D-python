import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Form, Input, Button, Card, Space, Typography, Tag,
  Spin, Alert, Divider, Popconfirm, Tooltip, message, Row, Col
} from 'antd'
import {
  ArrowLeftOutlined, PlusOutlined, ArrowUpOutlined, ArrowDownOutlined,
  EditOutlined, DeleteOutlined, PlayCircleOutlined, StopOutlined
} from '@ant-design/icons'
import { surveysApi } from '../api/surveys'
import QuestionEditorModal from '../components/survey/QuestionEditorModal'
import type { SurveyDetail, Question } from '../types/survey'

const { Title, Text } = Typography
const { TextArea } = Input

const Q_TYPE_LABEL: Record<string, string> = {
  text: '단답형', textarea: '장문형', radio: '단일선택',
  checkbox: '복수선택', scale: '척도', file: '파일',
}
const STATUS_COLOR: Record<string, string> = {
  draft: 'default', active: 'green', closed: 'red',
}
const STATUS_LABEL: Record<string, string> = {
  draft: '초안', active: '진행중', closed: '종료',
}

// 신규 생성 모드: id = 'new'
function AdminSurveyBuilderPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isNew = id === 'new'

  const [metaForm] = Form.useForm()
  const [survey, setSurvey] = useState<SurveyDetail | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(!isNew)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 질문 편집 모달
  const [modalOpen, setModalOpen] = useState(false)
  const [editingQuestion, setEditingQuestion] = useState<Question | undefined>()

  useEffect(() => {
    if (isNew) return
    surveysApi.get(Number(id))
      .then((res) => {
        setSurvey(res.data)
        setQuestions(res.data.questions ?? [])
        metaForm.setFieldsValue({
          title: res.data.title,
          description: res.data.description,
          start_date: res.data.start_date?.slice(0, 10) ?? '',
          end_date: res.data.end_date?.slice(0, 10) ?? '',
        })
      })
      .catch(() => setError('설문을 불러올 수 없습니다.'))
      .finally(() => setLoading(false))
  }, [id, isNew, metaForm])

  // ── 설문 메타 저장 ────────────────────────────────────

  const handleSaveMeta = async () => {
    const values = await metaForm.validateFields()
    setSaving(true)
    try {
      const payload = {
        title: values.title,
        description: values.description,
        start_date: values.start_date || undefined,
        end_date: values.end_date || undefined,
      }
      if (isNew) {
        const res = await surveysApi.create(payload)
        message.success('설문이 생성되었습니다.')
        navigate(`/admin/surveys/${res.data.id}/edit`, { replace: true })
      } else {
        const res = await surveysApi.update(Number(id), payload)
        setSurvey(res.data)
        message.success('설문이 저장되었습니다.')
      }
    } catch {
      message.error('저장 중 오류가 발생했습니다.')
    } finally {
      setSaving(false)
    }
  }

  // ── 상태 전환 ─────────────────────────────────────────

  const handleActivate = async () => {
    try {
      const res = await surveysApi.activate(Number(id))
      setSurvey(res.data)
      message.success('설문이 활성화되었습니다.')
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { error?: string } } })?.response?.data?.error
      message.error(msg ?? '활성화 중 오류가 발생했습니다.')
    }
  }

  const handleClose = async () => {
    try {
      const res = await surveysApi.close(Number(id))
      setSurvey(res.data)
      message.success('설문이 종료되었습니다.')
    } catch {
      message.error('종료 중 오류가 발생했습니다.')
    }
  }

  // ── 질문 CRUD ─────────────────────────────────────────

  const openAddModal = () => {
    setEditingQuestion(undefined)
    setModalOpen(true)
  }

  const openEditModal = (q: Question) => {
    setEditingQuestion(q)
    setModalOpen(true)
  }

  const handleModalOk = async (data: {
    question_type: string; question_text: string
    is_required: boolean; options?: string[]
  }) => {
    const surveyId = Number(id)
    if (editingQuestion) {
      const res = await surveysApi.updateQuestion(surveyId, editingQuestion.id, data)
      setQuestions((prev) => prev.map((q) => q.id === editingQuestion.id ? res.data : q))
      message.success('질문이 수정되었습니다.')
    } else {
      const res = await surveysApi.addQuestion(surveyId, data)
      setQuestions((prev) => [...prev, res.data])
      message.success('질문이 추가되었습니다.')
    }
    setModalOpen(false)
  }

  const handleDeleteQuestion = async (questionId: number) => {
    await surveysApi.deleteQuestion(Number(id), questionId)
    setQuestions((prev) => prev.filter((q) => q.id !== questionId))
    message.success('질문이 삭제되었습니다.')
  }

  const handleMoveQuestion = async (idx: number, direction: 'up' | 'down') => {
    const next = [...questions]
    const swapIdx = direction === 'up' ? idx - 1 : idx + 1
    ;[next[idx], next[swapIdx]] = [next[swapIdx], next[idx]]
    const reordered = next.map((q, i) => ({ ...q, order_num: i + 1 }))
    setQuestions(reordered)
    await surveysApi.reorderQuestions(
      Number(id),
      reordered.map((q) => ({ id: q.id, order_num: q.order_num }))
    )
  }

  const isDraft = !survey || survey.status === 'draft'

  if (loading) return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* 헤더 */}
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/admin')}>
          대시보드
        </Button>
        <Title level={4} style={{ margin: 0 }}>
          {isNew ? '새 설문 만들기' : '설문 편집'}
        </Title>
        {survey && (
          <Tag color={STATUS_COLOR[survey.status]}>{STATUS_LABEL[survey.status]}</Tag>
        )}
      </Space>

      {/* 설문 메타 정보 */}
      <Card
        title="설문 기본 정보"
        extra={
          <Space>
            {!isNew && survey?.status === 'draft' && (
              <Popconfirm
                title="설문을 활성화하면 응답을 받을 수 있습니다. 진행하시겠습니까?"
                onConfirm={handleActivate}
                okText="활성화"
                cancelText="취소"
              >
                <Button type="primary" icon={<PlayCircleOutlined />} size="small">
                  활성화
                </Button>
              </Popconfirm>
            )}
            {!isNew && survey?.status === 'active' && (
              <Popconfirm
                title="설문을 종료하면 더 이상 응답을 받을 수 없습니다."
                onConfirm={handleClose}
                okText="종료"
                cancelText="취소"
                okButtonProps={{ danger: true }}
              >
                <Button danger icon={<StopOutlined />} size="small">
                  설문 종료
                </Button>
              </Popconfirm>
            )}
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        <Form form={metaForm} layout="vertical">
          <Form.Item
            name="title"
            label="설문 제목"
            rules={[{ required: true, message: '제목을 입력하세요.' }]}
          >
            <Input placeholder="설문 제목을 입력하세요." maxLength={200} showCount disabled={!isDraft} />
          </Form.Item>
          <Form.Item name="description" label="설명 (선택)">
            <TextArea rows={2} placeholder="설문 목적이나 안내사항을 입력하세요." maxLength={1000} disabled={!isDraft} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="start_date" label="시작일 (선택)">
                <Input type="date" disabled={!isDraft} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="end_date" label="종료일 (선택)">
                <Input type="date" disabled={!isDraft} />
              </Form.Item>
            </Col>
          </Row>
          {isDraft && (
            <Button type="primary" onClick={handleSaveMeta} loading={saving}>
              {isNew ? '설문 생성' : '저장'}
            </Button>
          )}
        </Form>
      </Card>

      {/* 질문 목록 (신규 생성 전에는 숨김) */}
      {!isNew && (
        <Card
          title={`질문 목록 (${questions.length}개)`}
          extra={
            isDraft && (
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={openAddModal}
                size="small"
              >
                질문 추가
              </Button>
            )
          }
        >
          {questions.length === 0 && (
            <Text type="secondary">질문이 없습니다. 질문을 추가하세요.</Text>
          )}

          <Space direction="vertical" style={{ width: '100%' }}>
            {questions.map((q, idx) => (
              <Card
                key={q.id}
                size="small"
                style={{ background: '#fafafa' }}
                bodyStyle={{ padding: '10px 16px' }}
              >
                <Row align="middle" gutter={8}>
                  <Col flex="none">
                    <Text type="secondary" style={{ width: 28, display: 'inline-block' }}>
                      {idx + 1}.
                    </Text>
                  </Col>
                  <Col flex="auto">
                    <Space>
                      <Text strong>{q.question_text}</Text>
                      <Tag>{Q_TYPE_LABEL[q.question_type] ?? q.question_type}</Tag>
                      {q.is_required && <Tag color="red">필수</Tag>}
                    </Space>
                    {q.options && q.options.length > 0 && (
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          선택지: {q.options.join(', ')}
                        </Text>
                      </div>
                    )}
                  </Col>
                  {isDraft && (
                    <Col flex="none">
                      <Space>
                        <Tooltip title="위로">
                          <Button
                            size="small" type="text"
                            icon={<ArrowUpOutlined />}
                            disabled={idx === 0}
                            onClick={() => handleMoveQuestion(idx, 'up')}
                          />
                        </Tooltip>
                        <Tooltip title="아래로">
                          <Button
                            size="small" type="text"
                            icon={<ArrowDownOutlined />}
                            disabled={idx === questions.length - 1}
                            onClick={() => handleMoveQuestion(idx, 'down')}
                          />
                        </Tooltip>
                        <Tooltip title="수정">
                          <Button
                            size="small" type="text"
                            icon={<EditOutlined />}
                            onClick={() => openEditModal(q)}
                          />
                        </Tooltip>
                        <Tooltip title="삭제">
                          <Popconfirm
                            title="이 질문을 삭제하시겠습니까?"
                            onConfirm={() => handleDeleteQuestion(q.id)}
                            okText="삭제" cancelText="취소"
                            okButtonProps={{ danger: true }}
                          >
                            <Button size="small" type="text" danger icon={<DeleteOutlined />} />
                          </Popconfirm>
                        </Tooltip>
                      </Space>
                    </Col>
                  )}
                </Row>
              </Card>
            ))}
          </Space>

          {isDraft && questions.length > 0 && (
            <>
              <Divider />
              <Button type="dashed" icon={<PlusOutlined />} onClick={openAddModal} block>
                질문 추가
              </Button>
            </>
          )}
        </Card>
      )}

      <QuestionEditorModal
        open={modalOpen}
        initialData={editingQuestion}
        onOk={handleModalOk}
        onCancel={() => setModalOpen(false)}
      />
    </div>
  )
}

export default AdminSurveyBuilderPage
