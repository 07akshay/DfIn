token_int = 't_int'
token_float = 't_float'
token_plus = 'plus'
token_minus = 'minus'
token_mul = 'mul'
token_div = 'div'
token_leftp = 'lparen'
token_rightp = 'rparen'
number = '0123456789'

class Token:
	def __init__(self, token_type, value = None, pos_start = None, pos_end = None):
		self.type = token_type
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()


	def __repr__(self):
		if self.value:
			return f'{self.type}:{self.value}'
		else:
			return f'{self.type}'

class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
		# self.as_string()

	def as_string(self):
		result = f'{self.error_name}: {self.details}'
		result += f'{self.pos_start.fn}, line {self.pos_start.ln + 1}'
		# result += '\n\n' + string_with_arrows(self.pos_start.fttx, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):
	def __init__(self,pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self,pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, current_char):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.advance()

	def advance(self):
		self.pos.advance(self.current_char)
		if self.pos.idx < len(self.text):
			self.current_char = self.text[self.pos.idx]
		else:
			self.current_char = None

	def make_tokens(self):
		tokens = list()

		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance()
			elif self.current_char in number:
				tokens.append(self.make_number())
				# self.advance()
			elif self.current_char == '+':
				tokens.append(Token(token_plus))
				self.advance()
			elif self.current_char == '-':
				tokens.append(Token(token_minus))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token(token_mul))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(token_div))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(token_leftp))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(token_rightp))
				self.advance()
			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [], IllegalCharError(pos_start,self.pos,"'" + char + "'")

		return tokens, None


	def make_number(self):
		num = ''
		dot_cnt = 0

		while self.current_char != None and self.current_char in number+'.':
			if self.current_char == '.':
				if dot_cnt == 1:
					break
				dot_cnt += 1
				num += '.'

			else:
				num += self.current_char
			self.advance()

		if dot_cnt == 0:
			return Token(token_int, int(num))
		else:
			return Token(token_float, float(num))


class NumberNode:
	def __init__(self, tok):
		self.tok = tok
		# self.pos_start = self.tok.pos_start
		# self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.right_node = right_node
		self.op_tok = op_tok

		# self.pos_start = self.left_node.pos_start
		# self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		# self.pos_start = self.op_tok.pos_start
		# self.pos_end = self.op_tok.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]

		return self.current_tok

	def parse(self):
		res = self.expr()
		return res


	def factor(self):
		tok = self.current_tok
		if tok.type in (token_plus, token_minus):
			self.advance()
			factor = self.factor()
			return UnaryOpNode(tok, factor)
		if tok.type in (token_int, token_float):
			self.advance()
			return NumberNode(tok)
		if tok.type == token_leftp:
			self.advance()
			expr = self.expr()
			if self.current_tok.type == token_rightp:
				self.advance()
				return expr
		return

	def term(self):
		return self.bin_op(self.factor,(token_mul, token_div))


	def expr(self):
		return self.bin_op(self.term,(token_plus, token_minus))

	def bin_op(self, func, ops):
		left = func()
		while self.current_tok.type in ops:
			op_tok = self.current_tok
			self.advance()
			right = func()
			left = BinOpNode(left, op_tok, right)

		return left


class Number:
	def __init__(self, value):
		self.value = value

	def set_pos(self, pos_start = None, pos_end = None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def add_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value)

	def sub_to(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value)

	def mul_to(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value)

	def div_to(self, other):
		if isinstance(other, Number):
			return Number(self.value / other.value)

	def __repr__(self):
		return f'{self.value}'



class Interpreter:
	def visit(self,node):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node)

	def no_visit_method(self, node):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_NumberNode(self,node):
		# print(Number(node.tok.value))
		return Number(node.tok.value)
    
	def visit_BinOpNode(self,node):
		left = self.visit(node.left_node)
		right = self.visit(node.right_node)
		# print(node.op_tok)
		if node.op_tok.type == token_plus:
			# print("inside plus")
			result = left.add_to(right)

		elif node.op_tok.type == token_minus:
			result = left.sub_to(right)
		elif node.op_tok.type == token_mul:
			result = left.mul_to(right)
		elif node.op_tok.type == token_div:
			result = left.div_to(right)
		# print(result)
		return result

	def visit_UnaryOpNode(self,node):
		# print("Unary Node")
		num = self.visit(node.node)
		if node.op_tok.type == token_minus:
			num = num.mul_to(Number(-1))

		return num


def run(fn, text):
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()

	if error:
		return None, error

	parser = Parser(tokens)
	ast = parser.parse()

	interpreter = Interpreter()

	result = interpreter.visit(ast)

	return result, None

