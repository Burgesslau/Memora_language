# Testing Guide

本项目使用 **Vitest** 和 **React Testing Library** 进行单元测试和集成测试。

## 测试框架设置

- **Vitest**: 现代 Vite 原生测试框架，更轻量化和快速
- **React Testing Library**: 用户行为驱动的 React 组件测试
- **jsdom**: DOM 环境模拟

## 安装依赖

```bash
cd frontend
npm install
```

## 运行测试

### 运行所有测试
```bash
npm test
```

### 运行特定测试文件
```bash
npm test -- src/app/dashboard/grammar/page.test.tsx
```

### 监视模式（自动重新运行）
```bash
npm test -- --watch
```

### UI 界面运行测试
```bash
npm run test:ui
```

### 生成测试覆盖率报告
```bash
npm run test:coverage
```

## 测试文件位置

测试文件位于各组件和页面同目录，命名约定：
- `*.test.tsx` - React 组件测试
- `*.test.ts` - 工具函数测试

### 已添加的测试

#### 1. Grammar Dashboard 页面集成测试
- **文件**: `src/app/dashboard/grammar/page.test.tsx`
- **测试项**:
  - ✓ 页面标题和副标题渲染
  - ✓ 语法点列表显示
  - ✓ 进度条与掌握度百分比
  - ✓ 快速操作卡片
  - ✓ 仅显示语法点而不显示概念节点

#### 2. EvaluationResult 组件测试
- **文件**: `src/components/grammar/evaluation-result.test.tsx`
- **测试项**:
  - ✓ 通过/未通过徽章
  - ✓ 反馈信息显示
  - ✓ 结构评分和错误计数
  - ✓ 自由模式下的静默错误
  - ✓ 严谨模式下的错误标签

#### 3. InlineHighlight 组件测试
- **文件**: `src/components/grammar/inline-highlight.test.tsx`
- **测试项**:
  - ✓ 无错误时的文本渲染
  - ✓ 错误跨度高亮
  - ✓ 悬停提示中的建议显示
  - ✓ 多个错误跨度处理
  - ✓ 高亮之间的文本保留

#### 4. KpiCard 共享组件测试
- **文件**: `src/components/shared/kpi-card.test.tsx`
- **测试项**:
  - ✓ 标题和数值渲染
  - ✓ 副标题的有条件显示
  - ✓ 高亮样式应用
  - ✓ Lucide 图标渲染
  - ✓ 字符串和数值格式化

#### 5. 工具函数测试
- **文件**: `src/lib/utils.test.ts`
- **测试项**:
  - ✓ `masteryToStatus()` - 掌握度分级
  - ✓ `masteryToColor()` - 色彩映射
  - ✓ `masteryToScale()` - 缩放因子
  - ✓ `formatPercent()` - 百分比格式化

## 测试最佳实践

1. **测试命名**: 使用描述性名称清晰表达测试意图
2. **AAA 模式**: Arrange（准备）→ Act（行动）→ Assert（断言）
3. **避免实现细节**: 测试用户可见的行为而非内部实现
4. **独立性**: 每个测试应该独立运行，不依赖其他测试
5. **覆盖边界情况**: 测试正常路径、边界值和错误情况

## 示例测试写法

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<Component prop="value" />);
    expect(screen.getByText('expected text')).toBeInTheDocument();
  });
});
```

## CI/CD 集成

在 CI/CD 流程中运行测试：

```bash
npm test -- --run  # 非监视模式一次性运行
npm run test:coverage  # 生成覆盖率报告
```

## 常见问题

### Q: 如何调试失败的测试？
A: 在测试中添加 `console.log()` 或使用 `screen.debug()` 来检查 DOM 状态。

### Q: 如何模拟外部依赖？
A: 使用 `vitest` 的 `vi.mock()` 来模拟模块或函数。

### Q: 为什么测试找不到元素？
A: 检查组件是否渲染了预期的内容，使用 `screen.logTestingPlaygroundURL()` 调试。

## 扩展测试

添加新的测试用例时：
1. 在组件同目录创建 `*.test.tsx` 或 `*.test.ts` 文件
2. 导入必要的测试库和工具
3. 编写测试用例
4. 运行 `npm test` 验证
