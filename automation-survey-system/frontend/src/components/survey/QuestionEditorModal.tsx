import { useEffect, useState } from 'react'
import { Modal, Form, Input, Select, Switch, Button, Space, Typography } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import type { Question } from '../../types/survey'

const { Text } = Typography
const { TextArea } = Input

const QUESTION_TYPE_OPTIONS = [
  { value: 'text', label: '단답형 (텍스트)' },
  { value: 'textarea', label: '장문형 (텍스트)' },
  { value: 'radio', label: '단일 선택 (라디오)' },
  { value: 'checkbox', label: '복수 선택 (체크박스)' },
  { value: 'scale', label: '척도 (1~5점)' },
]

interface Props {
  open: boolean
  initialData?: Partial<Question>  // 수정 시 기존 값
  onOk: (data: {
    question_type: string
    question_text: string
    is_required: boolean
    options?: string[]
  }) => Promise<void>
  onCancel: () => void
}

function QuestionEditorModal({ open, initialData, onOk, onCancel }: Props) {
  const [form] = Form.useForm()
  const [qType, setQType] = useState<string>(initialData?.question_type ?? 'text')
  const [options, setOptions] = useState<string[]>(initialData?.options ?? ['', ''])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (open) {
      form.setFieldsValue({
        question_text: initialData?.question_text ?? '',
        question_type: initialData?.question_type ?? 'text',
        is_required: initialData?.is_required ?? true,
      })
      setQType(initialData?.question_type ?? 'text')
      setOptions(initialData?.options ?? ['', ''])
    }
  }, [open, initialData, form])

  const handleOk = async () => {
    const values = await form.validateFields()
    setSaving(true)
    try {
      await onOk({
        question_type: values.question_type,
        question_text: values.question_text,
        is_required: values.is_required,
        options: ['radio', 'checkbox'].includes(values.question_type)
          ? options.filter((o) => o.trim())
          : undefined,
      })
      form.resetFields()
    } finally {
      setSaving(false)
    }
  }

  const updateOption = (idx: number, value: string) => {
    const next = [...options]
    next[idx] = value
    setOptions(next)
  }

  const addOption = () => setOptions([...options, ''])
  const removeOption = (idx: number) => setOptions(options.filter((_, i) => i !== idx))

  const isChoiceType = qType === 'radio' || qType === 'checkbox'

  return (
    <Modal
      title={initialData?.id ? '질문 수정' : '질문 추가'}
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText={initialData?.id ? '저장' : '추가'}
      cancelText="취소"
      confirmLoading={saving}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="question_type"
          label="질문 유형"
          rules={[{ required: true }]}
        >
          <Select
            options={QUESTION_TYPE_OPTIONS}
            onChange={(v) => setQType(v)}
          />
        </Form.Item>

        <Form.Item
          name="question_text"
          label="질문 내용"
          rules={[{ required: true, message: '질문 내용을 입력하세요.' }]}
        >
          <TextArea rows={3} placeholder="질문을 입력하세요." maxLength={500} showCount />
        </Form.Item>

        <Form.Item name="is_required" label="필수 응답" valuePropName="checked">
          <Switch checkedChildren="필수" unCheckedChildren="선택" />
        </Form.Item>

        {/* radio / checkbox 선택지 편집 */}
        {isChoiceType && (
          <Form.Item label="선택지">
            <Space direction="vertical" style={{ width: '100%' }}>
              {options.map((opt, idx) => (
                <Space key={idx} style={{ width: '100%' }}>
                  <Text type="secondary" style={{ width: 24 }}>{idx + 1}.</Text>
                  <Input
                    value={opt}
                    placeholder={`선택지 ${idx + 1}`}
                    onChange={(e) => updateOption(idx, e.target.value)}
                    style={{ flex: 1 }}
                  />
                  {options.length > 2 && (
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => removeOption(idx)}
                    />
                  )}
                </Space>
              ))}
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={addOption}
                block
              >
                선택지 추가
              </Button>
            </Space>
          </Form.Item>
        )}

        {qType === 'scale' && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            1 (전혀 그렇지 않다) ~ 5 (매우 그렇다) 척도로 자동 설정됩니다.
          </Text>
        )}
      </Form>
    </Modal>
  )
}

export default QuestionEditorModal
