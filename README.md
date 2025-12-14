# personal-easy-demo
基础简易小项目 智能客服系统  
运行根目录run.py即可启动  
将想要加入知识库的文件加载至data/knowledge_base文件夹中  
运行date/knowledge_training/knowledge_train.py即可将文件嵌入到redis中（只创建了读取txt文件的方法）  
项目前端为使用gredio创建的简易网页，可以在输入框中输入自己的问题与智能客服交谈  
目前只包含了主要功能的部分示例，包括tool工具调用，智能体短期记忆，知识库检索，简易工单文件的生成  
智能体的每次生成都使用简单llm进行质量评估，并在终端输出  
由于功能过于简单没有进行MCP的调用  
