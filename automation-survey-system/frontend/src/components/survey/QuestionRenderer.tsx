import { Form, Input, Radio, Checkbox, Slider, Typography } from 'antd'
import type { Question } from '../../types/survey'

const { TextArea } = Input
const { Text } = Typography

interface Props {
  question: Question
  index: number
}

// scale 질문용 1~5 레이블
const SCALE_MARKS = { 1: '1', 2: '2', 3: '3', 4: '4', 5: '5' }

function QuestionRenderer({ question, index }: Props) {
  const label = (
    <span>
      <Text strong>{index + 1}. {question.question_text}</Text>
      {question.is_required && <Text type="danger"> *</Text>}
    </span>
  )

  const rules = question.is_required
    ? [{ required: true, message: '필수 항목입니다.' }]
    : []

  const fieldName = `q_${question.id}`

  return (
    <Form.Item
      name={fieldName}
      label={label}
      rules={rules}
      colon={false}
      style={{ marginBottom: 28 }}
    >
      {renderInput(question)}
    </Form.Item>
  )
}

function renderInput(question: Question) {
  switch (question.question_type) {
    case 'text':
      return <Input placeholder="답변을 입력하세요." maxLength={500} />

    case 'textarea':
      return (
        <TextArea
          placeholder="답변을 입력하세요."
          rows={4}
          maxLength={2000}
          showCount
        />
      )

    case 'radio': {
      const options = question.options ?? []
      return (
        <Radio.Group style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {options.map((opt) => (
            <Radio key={opt} value={opt}>{opt}</Radio>
          ))}
        </Radio.Group>
      )
    }

    case 'checkbox': {
      const options = question.options ?? []
      return (
        <Checkbox.Group style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {options.map((opt) => (
            <Checkbox key={opt} value={opt}>{opt}</Checkbox>
          ))}
        </Checkbox.Group>
      )
    }

    case 'scale':
      return (
        <div style={{ padding: '0 8px' }}>
          <Slider
            min={1}
            max={5}
            marks={SCALE_MARKS}
            step={1}
            style={{ width: 300 }}
          />
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            1 = 전혀 그렇지 않다 &nbsp;·&nbsp; 5 = 매우 그렇다
          </Typography.Text>
        </div>
      )

    case 'file':
      // Phase 5(화면 녹화)에서 통합 예정 — 현재 미지원
      return <Text type="secondary">파일 첨부는 현재 지원하지 않습니다.</Text>

    default:
      return <Input placeholder="답변을 입력하세요." />
  }
}

export default QuestionRenderer
