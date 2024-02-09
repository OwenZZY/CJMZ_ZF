from __future__ import annotations

import sys
import copy


class Node:
    def __init__(self, obj, nxt=None, prev=None):
        self.obj = obj
        self.next:Node = nxt
        self.prev:Node = prev

    def get_self(self):
        return self.obj

    def get_next_node(self) -> Node:
        return self.next

    def get_prev_node(self) -> Node:
        return self.prev

    def get_next(self):
        return self.next.get_self()

    def get_prev(self):
        return self.next.get_self()

    def set_self(self, obj):
        self.obj = obj

    def set_next(self, next_obj):
        next = Node(next_obj)
        self.set_next_node(next)

    def set_next_node(self, nextNode:Node):
        self.next = nextNode
        nextNode.prev = self

    def set_prev(self, prev_obj):
        prev = Node(prev_obj)
        self.set_prev_node(prev)

    def set_prev_node(self, prevNode:Node):
        self.prev = prevNode
        prevNode.next = self

    def __str__(self):
        return str(self.obj)

class LinkedList:
    def __init__(self, init_obj=None):
        self.head:Node = None
        self.tail:Node = None
        self.size = 0
        if init_obj is None:
            return
        if not isinstance(init_obj, Node):
            init_node = Node(init_obj)
        else:
            init_node = init_obj
        self.head = init_node
        self.tail = self.head
        self.size = 1

    def append(self, obj):
        if self.size == 0:
            node = Node(obj)
            self.head = node
            self.tail = self.head
        self.tail.set_next(obj)
        self.tail = self.tail.next
        self.size += 1
        return self.tail.get_self()

    def append_node(self, node:Node):
        if self.size == 0:
            self.head = node
            self.tail = self.head
            return
        self.tail.set_next_node(node)
        size_inc = 0
        curr = self.tail
        while curr is not None:
            curr = curr.next
            size_inc += 1
        self.tail = node
        self.size += size_inc
        return self.tail.get_self()

    def extend_LL(self, L):
        L:LinkedList
        if self.size == 0:
            self.head = L.head
            self.tail = L.tail
            self.size = L.size
            return
        self.tail.set_next(L.head)
        self.tail = L.tail
        self.size = self.size + L.size
        return

    def insert(self, obj, index = 0):
        node = Node(obj)
        if self.size == 0:
            self.append_node(node)
            self.size+=1
            return
        self.insert_node(node, index)
        self.size += 1

    # insert at i-th position (0-indexed)
    def insert_node(self, node:Node, index=0):
        if self.size == 0:
            self.append_node(node)
            return
        if self.size < index:
            print("Index out of range!")
            sys.exit(0)
        curr:Node = self.head
        for _ in range(index):
            curr = curr.get_next_node()
        if index == 0:
            self.head = node
        curr.set_prev_node(node)


    def copy_a_reverse(self):
        # print('Copy a reverse', self)
        L = LinkedList()
        curr = self.head
        while curr is not None:
            L.insert(curr.get_self())
            curr:Node = curr.get_next_node()
        # print('A reverse is copied', L)
        return L

    def concatenate(self, other:LinkedList):
        # concatenate two linkedlists
        # make sure that self.tail == other.head
        if self.size == 0 or other.size == 0:
            print('Linkedlist length of zero')
            sys.exit(0)
        if self.tail.get_self() != other.head.get_self():
            print('Head-tail does not match!')
            sys.exit()
        self.size += other.size - 1
        if other.size == 1:
            self.append(other.head.get_self())
            return self.tail.get_self()
        self.tail.set_next_node(other.head.next)
        self.tail = other.tail
        return self.tail.get_self()

    def concatenate_from_before(self, other:LinkedList):
        if self.size == 0 or other.size == 0:
            print('Linkedlist length of zero')
            sys.exit(0)
        # if the case is that two nodes are different but
        if  other.tail.get_self() != self.head.get_self():
            print('Head-tail does not match!')
            sys.exit()
        self.size += other.size - 1
        if other.size == 1:
            self.insert(other.head.get_self())
            self.head = other.head
            return self.head.get_self()
        self.head.set_prev_node(other.tail.prev)
        self.head = other.head
        return self.head.get_self()

    def trim_head(self):
        if self.size == 0:
            print('Empty already')
            sys.exit(0)
        if self.size == 1:
            self.head, self.tail, self.size = None, None, 0
            return None
        self_head:Node = self.head
        self.head = self_head.next
        self.head.prev = None
        self.size -= 1
        return self.head.get_self()


    def trim_tail(self):
        if self.size == 0:
            print('Empty already')
            sys.exit(0)
        if self.size == 1:
            self.head, self.tail, self.size = None, None, 0
            return None
        self_tail:Node = self.tail
        self.tail = self_tail.prev
        self.tail.next = None
        self.size -= 1
        return self.tail.get_self()


    def __str__(self):
        if self.size == 0:
            return 'NULL'
        # ret = 'NULL ->'
        ret = ' '
        curr = self.head
        while curr is not None:
            ret += str(curr) + ' ->'
            curr = curr.next
        # ret += ' Null'
        return ret







